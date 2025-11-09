import math
from enum import Enum

import stripe
import structlog
from django.conf import settings
from django.core.cache import cache, caches
from django.utils import timezone
from pydantic import BaseModel

from agora.keycloak_admin import keycloak_admin

from .models import AgoraUser, IdentityVerification, WaitingList

logger = structlog.get_logger(__name__)


class DocumentTypeEnum(str, Enum):
    PASSPORT = "passport"
    DRIVING_LICENSE = "driving_license"
    ID_CARD = "id_card"


class DateOfBirth(BaseModel):
    day: int | None
    month: int | None
    year: int | None


class VerifiedDocDetails(BaseModel):
    first_name: str | None
    last_name: str | None
    issuing_country: str | None
    document_type: DocumentTypeEnum | None
    date_of_birth: DateOfBirth | None


def round_to_nearest(n, m):
    return m * math.floor(n / m)


def format_waiting_list_count(count: int) -> int:
    if count < 100:
        return round_to_nearest(count, 10)
    elif count < 1000:
        return round_to_nearest(count, 100)
    else:
        return round_to_nearest(count, 1000)


def get_waiting_list_count(*, cache_timeout: int = 300) -> int:
    """
    Get the count of waiting list entries with caching.

    Args:
        cache_timeout: Cache timeout in seconds (default: 5 minutes)

    Returns:
        Number of waiting list entries
    """
    cache_key = "waiting_list_count"

    # Try to get from cache first
    count = cache.get(cache_key)

    if count is None:
        # Cache miss - fetch from database
        count = WaitingList.objects.count()
        # Round the count to the nearest 10
        count = format_waiting_list_count(count)
        # Store in cache with timeout
        cache.set(cache_key, count, cache_timeout)

    return count


def is_user_identity_recently_verified(user: AgoraUser) -> bool:
    """
    Check if the user has a verified identity within the last year.
    """
    return user.identity_verifications.filter(  # pyright: ignore[reportAttributeAccessIssue]
        status=IdentityVerification.IdentityVerificationStatus.VERIFIED,
        created_at__gte=timezone.now() - timezone.timedelta(days=365),
    ).exists()


def get_waiting_list_entry(*, email: str, invite_code: str | None) -> WaitingList | None:
    """
    Retrieve a waiting list entry by email and invite code.

    Args:
        email: The email address associated with the waiting list entry.
        invite_code: The unique invite code for the waiting list entry.
    Returns:
        The WaitingList entry if found, otherwise None.
    """

    try:
        if invite_code:
            return WaitingList.objects.get(
                invite_sent_at__isnull=False,
                invite_accepted_at__isnull=True,
                email=email,
                invite_code=invite_code,
            )
        else:
            return WaitingList.objects.get(
                invite_sent_at__isnull=False,
                invite_accepted_at__isnull=True,
                email=email,
            )
    except WaitingList.DoesNotExist:
        return None


def is_user_profile_complete(user: AgoraUser) -> bool:
    """
    Check if the user has completed their profile (handle is set).

    The user's name will be set from Keycloak which receives it from the
    identity verification service (read from the ID).

    Args:
        user: The user to check

    Returns:
        True if profile is complete, False otherwise
    """
    return bool(user.handle)


def get_identity_verification_for_user(*, user: AgoraUser) -> IdentityVerification | None:
    """
    Get the latest identity verification record for the user.

    Args:
        user: The user to get the identity verification for
    Returns:
        The latest IdentityVerification record or None if not found
    """
    return IdentityVerification.objects.filter(user=user).order_by("-updated_at").first()


def get_stripe_customer(*, email: str) -> stripe.Customer | None:
    """
    Get the Stripe customer for the user.
    """
    customers = stripe.Customer.search(query=f"email:'{email}'")
    if customers.data and len(customers.data) > 0:
        return customers.data[0]
    return None


def get_external_verification_details(
    *, identity_verification: IdentityVerification
) -> VerifiedDocDetails | None:
    """
    Get the external verification details for the identity verification.

    This function uses a restricted Stripe client to fetch the verification details and
    a restricted cache to store the results.
    """

    restricted_cache = caches["stripe_restricted"]

    cache_key = f"external_verification_details_{identity_verification.id}"

    cached_details = restricted_cache.get(cache_key)
    if cached_details:
        return cached_details

    if identity_verification.service == IdentityVerification.IdentityVerificationService.STRIPE:
        session = get_stripe_verification_session_and_report(
            stripe_verification_session_id=identity_verification.external_id
        )

        if session.status != "verified":
            return None

        last_verification_report = session.last_verification_report
        document = last_verification_report.document

        if document.status != "verified":
            return None

        dob = document.get("dob", {})

        details = VerifiedDocDetails(
            first_name=document.get("first_name", None),
            last_name=document.get("last_name", None),
            issuing_country=document.get("issuing_country", None),
            document_type=document.get("type", None),
            date_of_birth=DateOfBirth(
                day=dob.get("day", None),
                month=dob.get("month", None),
                year=dob.get("year", None),
            ),
        )
        restricted_cache.set(cache_key, details, timeout=300)
        return details
    else:
        return None


def get_stripe_verification_session_and_report(
    *, stripe_verification_session_id: str
) -> stripe.identity.VerificationSession | None:
    """
    Get the Stripe verification session and report for the verification session ID.

    Returns:
        The Stripe verification session and report if found, otherwise None.
    """

    restricted_stripe_client = stripe.StripeClient(
        api_key=settings.STRIPE_RESTRICTED_API_KEY,
    )
    session = restricted_stripe_client.v1.identity.verification_sessions.retrieve(
        session=stripe_verification_session_id,
        params={
            "expand": [
                "last_verification_report",
                "last_verification_report.document.sex",
                "last_verification_report.document.dob",
            ],
        },
    )
    return session


def get_stripe_verification_report(
    *, stripe_verification_report_id: str
) -> stripe.identity.VerificationReport | None:
    """
    Get the Stripe verification report for the verification report ID.
    """
    restricted_stripe_client = stripe.StripeClient(
        api_key=settings.STRIPE_RESTRICTED_API_KEY,
    )
    report = restricted_stripe_client.v1.identity.verification_reports.retrieve(
        report=stripe_verification_report_id,
        params={
            "expand": [
                "document.sex",
                "document.dob",
            ],
        },
    )
    return report


def get_keycloak_user(*, email: str) -> dict | None:
    """
    Get the Keycloak user for the user by email.

    Returns:
        The Keycloak user (a [`UserRepresentation`](https://www.keycloak.org/docs-api/latest/rest-api/index.html#UserRepresentation))if found, otherwise None.
    """  # noqa: E501
    matching_users = keycloak_admin.get_users(query={"email": email})
    if matching_users and len(matching_users) > 0:
        return matching_users[0]
    return None


def get_verification_history(*, user: AgoraUser) -> list[IdentityVerification]:
    """
    Get all identity verification attempts for a user, ordered by most recent first.

    Args:
        user: The user to get verification history for
    Returns:
        List of IdentityVerification records, ordered by updated_at descending
    """
    return list(IdentityVerification.objects.filter(user=user).order_by("-updated_at"))


def get_profile_stats(*, user: AgoraUser) -> dict:
    """
    Get profile completeness statistics for a user.

    Args:
        user: The user to get profile stats for
    Returns:
        Dictionary with profile statistics:
        - is_complete: bool
        - has_handle: bool
        - has_bio: bool
        - has_profile_image: bool
        - links_count: int
        - is_public: bool
    """
    profile = getattr(user, "profile", None)
    links_count = 0
    has_profile_image = False
    has_bio = False
    is_public = False

    if profile:
        links_count = profile.links.count()
        has_profile_image = bool(profile.profile_image)
        has_bio = bool(profile.bio)
        is_public = profile.is_public

    return {
        "is_complete": is_user_profile_complete(user),
        "has_handle": bool(user.handle),
        "has_bio": has_bio,
        "has_profile_image": has_profile_image,
        "links_count": links_count,
        "is_public": is_public,
    }
