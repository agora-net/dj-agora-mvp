from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.urls import NoReverseMatch, reverse


def stripe_identity_verification_flow(*, request: HttpRequest) -> str:
    """
    Get the Stripe identity verification flow ID for the current user.
    Returns the flow ID string or None if not set.

    Takes the request for future use so we can do things like A/B testing.
    """

    return settings.STRIPE_IDENTITY_VERIFICATION_FLOW


def is_named_url(url_string):
    """
    Check if a string is a named URL pattern.
    Returns True if it's a named URL, False if it's a path.
    """
    try:
        # Try to reverse the URL - if it works, it's a named URL
        reverse(url_string)
        return True
    except (NoReverseMatch, ImproperlyConfigured):
        return False
