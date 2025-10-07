import stripe
import structlog
from ninja import NinjaAPI, Schema
from ninja.security import django_auth

from agora import selectors

from .models import AgoraUser

# Use the fork of Django Ninja
# https://pmdevita.github.io/django-shinobi/
api = NinjaAPI(
    version="1.0.0",
    title="Agora API",
    description="API for the Agora platform.",
    csrf=True,
)

logger = structlog.get_logger(__name__)


class StripeIdentityResponse(Schema):
    client_secret: str


@api.post("/identity/stripe/", auth=django_auth, response={201: StripeIdentityResponse})
def create_stripe_identity_verification_session(request):
    # we know the user is authenticated because of the auth decorator on the API
    user: AgoraUser = request.user  # type: ignore

    logger.info("creating Stripe identity verification session", user_id=user.id)

    idempotency_key = selectors.stripe_idempotency_key_time_based(
        prefix="create_stripe_identity_verification_session",
        unique_key=request.session.session_key,
    )

    verification_session = stripe.identity.VerificationSession.create(
        verification_flow=selectors.stripe_identity_verification_flow(request=request),
        idempotency_key=idempotency_key,
        metadata={
            "user_id": str(user.id),
            "keycloak_id": str(user.keycloak_id),
        },
    )

    logger.info(
        "created Stripe identity verification session",
        user_id=user.id,
        id=verification_session.id,
    )
    return (201, verification_session)
