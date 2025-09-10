import secrets

import requests
from django.core.cache import cache
from django.db import IntegrityError

from agora.apps.core.models import WaitingList


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
