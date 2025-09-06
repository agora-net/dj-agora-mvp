import secrets

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
