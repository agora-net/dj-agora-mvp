import math

import stripe
import structlog
from django.conf import settings
from django.core.cache import cache, caches
from django.utils import timezone
from pydantic import BaseModel

from agora.colorthief import ColorThief

from .models import AgoraUser, IdentityVerification, WaitingList

logger = structlog.get_logger(__name__)


class DateOfBirth(BaseModel):
    day: int | None
    month: int | None
    year: int | None


class StripeVerificationDetails(BaseModel):
    first_name: str | None
    last_name: str | None
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
) -> StripeVerificationDetails | None:
    """
    Get the external verification details for the identity verification.

    This function uses a restricted Stripe client to fetch the verification details and
    a restricted cache to store the results.
    """

    restricted_cache = caches["stripe_restricted"]

    cache_key = f"external_verification_details_{identity_verification.id}"

    cached_details = restricted_cache.get(cache_key)
    if cached_details:
        return StripeVerificationDetails(**cached_details)

    restricted_stripe_client = stripe.StripeClient(
        api_key=settings.STRIPE_RESTRICTED_API_KEY,
    )

    if identity_verification.service == IdentityVerification.IdentityVerificationService.STRIPE:
        session = restricted_stripe_client.v1.identity.verification_sessions.retrieve(
            identity_verification.external_id,
            params={
                "expand": ["verified_outputs", "verified_outputs.dob"],
            },
        )

        dob = session.verified_outputs.get("dob", {})

        details = StripeVerificationDetails(
            first_name=session.verified_outputs.get("first_name", None),
            last_name=session.verified_outputs.get("last_name", None),
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


def get_dominant_color(*, image_filepath: str) -> tuple[int, int, int]:
    try:
        with open(image_filepath, "rb") as image_file:
            color_thief = ColorThief(image_file)
            return color_thief.get_color(quality=5)
    except Exception as e:
        logger.error(f"Error getting dominant color: {e}")
        return (0, 0, 0)
