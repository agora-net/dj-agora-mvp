import stripe
import structlog
from ninja import NinjaAPI, Schema
from ninja.security import django_auth

from agora import selectors

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
    logger.info("creating Stripe identity verification session")

    verification_session = stripe.identity.VerificationSession.create(
        verification_flow=selectors.stripe_identity_verification_flow(request=request),
    )

    logger.info("created Stripe identity verification session", id=verification_session.id)
    return (201, verification_session)
