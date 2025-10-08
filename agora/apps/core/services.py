import secrets

import requests
import stripe
import structlog
from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.db import IntegrityError
from django.http import Http404, HttpRequest
from django.template.loader import render_to_string
from django.utils import timezone
from keycloak import KeycloakGetError

from agora.keycloak_admin import keycloak_admin

from .models import AgoraUser, IdentityVerification, WaitingList

logger = structlog.get_logger(__name__)


def add_to_waiting_list(sanitized_email_address: str) -> WaitingList:
    """
    Add a sanitized email address to the waiting list.

    Args:
        sanitized_email_address: A clean, normalized email address

    Returns:
        WaitingList: The created waiting list entry

    Raises:
        IntegrityError: If the email already exists in the waiting list
        ValueError: If the email address is invalid
    """
    if not sanitized_email_address or not sanitized_email_address.strip():
        raise ValueError("Email address cannot be empty")

    # Generate a unique invite code
    invite_code = _generate_invite_code()

    try:
        waiting_list_entry = WaitingList.objects.create(
            email=sanitized_email_address,
            invite_code=invite_code,
        )
        # Pre-cache the position since it will be accessed immediately
        waiting_list_entry.pre_cache_position()
        # Clear the waiting_list_count cache
        cache.delete("waiting_list_count")
        return waiting_list_entry
    except IntegrityError as e:
        if "email" in str(e):
            raise IntegrityError("Email address already exists in waiting list") from e
        elif "invite_code" in str(e):
            # Retry with a new invite code if there's a collision
            invite_code = _generate_invite_code()
            waiting_list_entry = WaitingList.objects.create(
                email=sanitized_email_address,
                invite_code=invite_code,
            )
            # Pre-cache the position since it will be accessed immediately
            waiting_list_entry.pre_cache_position()
            return waiting_list_entry
        else:
            raise


def _generate_invite_code() -> str:
    """
    Generate a unique invite code.

    Returns:
        str: A unique invite code
    """
    return secrets.token_urlsafe(32)


def validate_cloudflare_turnstile(
    *,
    token: str,
    secret: str,
    remoteip: str | None = None,
) -> dict:
    """
    Validate a Cloudflare Turnstile token.

    Args:
        token: The token to validate
        secret: The secret key
        remoteip: The remote IP address
    """
    url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

    data = {"secret": secret, "response": token}

    if remoteip:
        data["remoteip"] = remoteip

    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Turnstile validation error: {e}")
        return {"success": False, "error-codes": ["internal-error"]}


def create_user_in_keycloak(
    *,
    sanitized_email: str,
) -> str:
    """
    Create a user in Keycloak.
    """
    try:
        new_user = keycloak_admin.create_user(
            payload={
                "email": sanitized_email,
                "emailVerified": False,  # The user will be verified in the next step
                "username": sanitized_email,
                "enabled": True,
            },
            exist_ok=False,
        )

        logger.info("new user created in Keycloak", user_id=new_user)

        return new_user
    except KeycloakGetError as e:
        raise ValueError("User already exists in Keycloak") from e


def add_invite_code_to_waiting_list_entry(
    *,
    waiting_list_entry: WaitingList,
) -> str:
    """
    Add an invite code to a waiting list entry if it doesn't already have one.
    """
    if not waiting_list_entry.invite_code:
        waiting_list_entry.invite_code = _generate_invite_code()
        waiting_list_entry.save()

    return waiting_list_entry.invite_code


def send_waiting_list_invite_email(
    *,
    email: str,
    waiting_list_entry: WaitingList,
    invite_url: str,
) -> None:
    """
    Send a waiting list invite email to the user.
    """
    logger.info(
        "sending waiting list invite email",
        entry=waiting_list_entry.type_id,
    )

    invite_code = add_invite_code_to_waiting_list_entry(
        waiting_list_entry=waiting_list_entry,
    )

    text_content = render_to_string(
        template_name="emails/waiting_list/invite_to_register.txt",
        context={
            "invite_url": invite_url,
            "invite_code": invite_code,
            "email": email,
            "support_email": settings.SUPPORT_EMAIL,
        },
    )

    try:
        msg = EmailMultiAlternatives(
            subject="Your invite to join Agora",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
            alternatives=[],
        )
        msg.send()

        logger.info(
            "waiting list invite email sent",
            entry=waiting_list_entry.type_id,
        )

        waiting_list_entry.invite_sent_at = timezone.now()
        waiting_list_entry.save()

    except Exception as e:
        raise ValueError("Failed to send waiting list invite email") from e


def send_user_registration_actions(
    *,
    user_id: str,
    redirect_uri: str,
) -> None:
    """
    Send registration actions to the user in Keycloak.
    """
    logger.info("sending registration actions to user", user_id=user_id)

    required_actions = [
        "VERIFY_EMAIL",
        "UPDATE_PASSWORD",
        "TERMS_AND_CONDITIONS",
    ]

    try:
        keycloak_admin.send_update_account(
            user_id=user_id,
            # Despite saying this should be a dict, it should actually be a list of actions
            # https://www.keycloak.org/docs-api/latest/javadocs/org/keycloak/models/UserModel.RequiredAction.html
            payload=required_actions,  # type: ignore
            lifespan=60 * 60 * 24 * 7,  # Link valid for 7 days
            client_id=settings.KEYCLOAK_CLIENT_ID,
            redirect_uri=redirect_uri,
        )
    except KeycloakGetError as e:
        raise ValueError("Failed to send registration actions email") from e


def register_user_in_keycloak(
    *,
    sanitized_email: str,
    redirect_uri: str,
) -> str:
    """
    Register a new user in Keycloak and send them registration actions.

    Args:
        sanitized_email: The user's email address
        redirect_uri: The URI to redirect to after registration actions.
            As must be whitelisted in Keycloak, recommend using similar to:
            `request.build_absolute_uri(reverse("home"))`
    Returns:
        str: The Keycloak user ID of the newly created user
    """
    user_id = create_user_in_keycloak(
        sanitized_email=sanitized_email,
    )

    send_user_registration_actions(user_id=user_id, redirect_uri=redirect_uri)

    return user_id


def expire_waiting_list_entry(
    *,
    waiting_list_entry: WaitingList,
) -> None:
    """
    Expire a waiting list entry by setting the invite_accepted_at timestamp.

    Args:
        waiting_list_entry: The WaitingList entry to expire
    """
    waiting_list_entry.invite_accepted_at = timezone.now()
    waiting_list_entry.save()
    # Clear the waiting_list_count cache
    cache.delete("waiting_list_count")


def fetch_identity_verification_details(
    *,
    verification_service: IdentityVerification.IdentityVerificationService,
    verification_external_id: str,
) -> dict | None:
    """
    Fetch identity verification details from the external service.

    Args:
        verification_service: The service used for verification
        verification_external_id: The external ID from the verification service
    Returns:
        dict | None: The verification details, or None if not found or error
    """
    if verification_service == IdentityVerification.IdentityVerificationService.STRIPE:
        try:
            session = stripe.identity.VerificationSession.retrieve(
                verification_external_id,
                expand=[
                    "last_verification_report",
                    "verified_outputs",
                    "verified_outputs.dob",
                    "verified_outputs.sex",
                ],
            )
            return session
        except stripe.StripeError as e:
            logger.error(
                "failed to fetch Stripe identity verification details",
                error=str(e),
                verification_external_id=verification_external_id,
            )
            return None
    else:
        logger.warning(
            "unsupported identity verification service for fetching details",
            verification_service=verification_service,
        )
        raise NotImplementedError(f"Fetching details for {verification_service} is not implemented")


def update_identity_verification_status(
    *,
    user: AgoraUser,
    verification_service: IdentityVerification.IdentityVerificationService,
    verification_external_id: str,
    status: IdentityVerification.IdentityVerificationStatus,
) -> None:
    """
    Update the identity verification status for a user.

    Args:
        user: The AgoraUser to update
        verification_service: The service used for verification
        verification_external_id: The external ID from the verification service
        status: The new status to set
    """
    IdentityVerification.objects.update_or_create(
        user=user,
        service=verification_service,
        external_id=verification_external_id,
        defaults={
            "status": status,
        },
    )

    # Also update in Keycloak metadata for OIDC sign-ins


def handle_stripe_identity_verification_event(
    *,
    request: HttpRequest,
    event: stripe.Event,
) -> None:
    """
    Handle a Stripe identity verification event.

    Args:
        request: The Django HTTP request object
        event: The Stripe event payload
    """

    if not event.type.startswith("identity.verification_session."):
        raise ValueError("Event type is not an identity verification event")

    session: stripe.identity.VerificationSession = event.data.object  # type: ignore

    user = AgoraUser.objects.get(id=session.metadata.get("user_id"))
    if not user:
        raise Http404("User not found for identity verification")

    status = None

    if event.type == "identity.verification_session.canceled":
        status = IdentityVerification.IdentityVerificationStatus.FAILED
    elif event.type == "identity.verification_session.created":
        logger.info(
            "received unhandled Stripe identity verification event type",
            event_type=event.type,
            event_id=event.id,
        )
    elif event.type == "identity.verification_session.processing":
        status = IdentityVerification.IdentityVerificationStatus.PROCESSING
    elif event.type == "identity.verification_session.requires_input":
        status = IdentityVerification.IdentityVerificationStatus.REQUIRES_ACTION
    elif event.type == "identity.verification_session.verified":
        status = IdentityVerification.IdentityVerificationStatus.VERIFIED

    if status:
        update_identity_verification_status(
            user=user,
            verification_service=IdentityVerification.IdentityVerificationService.STRIPE,
            verification_external_id=session.id,
            status=status,
        )
