from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch, reverse


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
