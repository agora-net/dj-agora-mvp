from django.core.exceptions import ValidationError
from django.urls.resolvers import string
from django.utils.translation import gettext_lazy as _

from agora.apps.core.models import AgoraUser


def validate_no_whitespace(value: str) -> None:
    """Validate that a string contains no whitespace characters."""
    if True in [c in value for c in string.whitespace]:
        raise ValidationError(_("Whitespace characters are not allowed.")) from None


def validate_handle_available(value: str, user=None) -> None:
    """Validate that a handle is available."""
    queryset = AgoraUser.objects.filter(handle=value)
    # If user is provided, exclude them from the check
    if user:
        queryset = queryset.exclude(id=user.id)
    if queryset.exists():
        raise ValidationError(_("Handle is already taken.")) from None
