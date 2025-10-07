import hashlib
from datetime import UTC, datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.urls import NoReverseMatch, reverse


def stripe_idempotency_key_time_based(*, prefix: str, unique_key: str) -> str:
    """
    Generate a time-based idempotency key for Stripe operations.
    The key is based on the given prefix, user ID, and current date (YYYYMMDD).
    This ensures that operations are idempotent within the same day for the same user.

    Args:
        prefix (str): A string prefix to identify the operation type (e.g., "create_charge").
        unique_key (str): A unique key to identify the user or session
            (e.g., user ID or session ID).
    Returns:
        str: A unique idempotency key string.
    """

    now = datetime.now(UTC)

    today_str = now.strftime("%Y%m%d")
    # select a 6 hour period so idempotency key changes 4 times a day
    hour_block = now.hour // 6

    unique_key = f"{prefix}_{unique_key}_{today_str}_{hour_block}"

    # MD5 hash the resulting string to shorten and obfuscate it
    hashed_key = hashlib.md5(unique_key.encode()).hexdigest()
    return hashed_key


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
