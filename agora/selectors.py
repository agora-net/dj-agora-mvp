import hashlib
import random
import string
from datetime import UTC, datetime

import stripe
import structlog
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.urls import NoReverseMatch, reverse

from agora.colorthief import ColorThief
from agora.constants import ADJECTIVES, NOUNS

logger = structlog.get_logger(__name__)


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
    hour_block = now.hour

    unique_key = f"{prefix}_{unique_key}_{today_str}_{hour_block}"

    # MD5 hash the resulting string to shorten and obfuscate it
    hashed_key = hashlib.md5(unique_key.encode()).hexdigest()
    return hashed_key


def contains_whitespace(s: str) -> bool:
    """
    Check if a string contains any whitespace characters.
    """
    return True in [c in s for c in string.whitespace]


def generate_unique_handle() -> str:
    """
    Generate a unique, URL friendly handle for a user.

    Will output something like "powerful-sphinx-1234"
    """

    adjective = random.choice(ADJECTIVES).lower()
    noun = random.choice(NOUNS).lower()
    numeric_hash = random.randint(1000, 9999)

    return f"{adjective}-{noun}-{numeric_hash}"


def stripe_identity_verification_flow(*, request: HttpRequest) -> str:
    """
    Get the Stripe identity verification flow ID for the current user.
    Returns the flow ID string or None if not set.

    Takes the request for future use so we can do things like A/B testing.
    """

    return settings.STRIPE_IDENTITY_VERIFICATION_FLOW


def stripe_donation_product_id() -> str:
    """
    Finds the Stripe product ID for the donation product.
    """
    cache_key = "stripe_donation_product_id"
    cached_product_id = cache.get(cache_key)
    if cached_product_id:
        return cached_product_id

    products = stripe.Product.search(query="active:'true' AND metadata['type']:'donation'")
    if not products.data or len(products.data) == 0:
        raise ValueError("No donation product found")

    # Find the latest updated product
    latest_product = max(products.data, key=lambda x: x.updated)

    cache.set(cache_key, latest_product.id, timeout=60 * 5)  # 5 minutes
    return latest_product.id


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


def get_dominant_color(*, image_filepath: str) -> tuple[int, int, int]:
    try:
        with open(image_filepath, "rb") as image_file:
            color_thief = ColorThief(image_file)
            return color_thief.get_color(quality=5)
    except Exception as e:
        logger.error(f"Error getting dominant color: {e}")
        return (0, 0, 0)
