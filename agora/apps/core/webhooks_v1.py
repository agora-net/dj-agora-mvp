import json

import stripe
import structlog
from django.conf import settings
from django.http import HttpRequest
from ninja import NinjaAPI, Schema
from ninja.responses import codes_4xx

from .services import (
    handle_stripe_checkout_session_completed,
    handle_stripe_identity_verification_event,
)

webhooks = NinjaAPI(
    version="1.0.0-webhooks",
    title="Agora Webhooks",
    description="Webhooks for the Agora platform.",
    csrf=False,  # Webhooks are called by external services, so CSRF is not applicable
)

logger = structlog.get_logger(__name__)


class StripeWebhookResponse(Schema):
    status: str


@webhooks.post(
    "/stripe/",
    auth=None,
    url_name="stripe_webhook",
    response={codes_4xx: StripeWebhookResponse, 200: StripeWebhookResponse},
)
def stripe_webhook(request: HttpRequest):
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError:
        # Invalid payload
        return 400, {"status": "invalid payload"}

    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except stripe.SignatureVerificationError as e:
        # Invalid signature
        logger.error("invalid Stripe webhook signature", error=str(e))
        return 400, {"status": "invalid signature"}

    # Handle the event
    logger.info("received Stripe webhook event", event_type=event.type, event_id=event.id)

    # https://docs.stripe.com/api/events/types#event_types-identity.verification_session.canceled
    if event.type.startswith("identity.verification_session."):
        handle_stripe_identity_verification_event(request=request, event=event)
    elif (
        event.type == "checkout.session.completed"
        or event.type == "checkout.session.async_payment_succeeded"
    ):
        handle_stripe_checkout_session_completed(request=request, event=event)
    else:
        logger.warning(
            "unhandled Stripe webhook event type",
            event_type=event.type,
            event_id=event.id,
        )

    return 200, {"status": "success"}
