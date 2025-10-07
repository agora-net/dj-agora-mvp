import stripe
from ninja import NinjaAPI, Schema
from ninja.security import django_auth

# Use the fork of Django Ninja
# https://pmdevita.github.io/django-shinobi/
api = NinjaAPI(
    version="1.0.0",
    title="Agora API",
    description="API for the Agora platform.",
    csrf=True,
)


class StripeIdentityResponse(Schema):
    client_secret: str


@api.post("/identity/stripe/", auth=django_auth, response={201: StripeIdentityResponse})
def create_stripe_identity_verification_session(request):
    verification_session = stripe.identity.VerificationSession.create()

    return (201, verification_session)
