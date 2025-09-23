import math

from django.core.cache import cache
from django.utils import timezone

from .models import AgoraUser, IdentityVerification, WaitingList


def round_to_nearest(n, m):
    return m * math.floor(n / m)


def format_waiting_list_count(count: int) -> int:
    if count < 100:
        return round_to_nearest(count, 10)
    elif count < 1000:
        return round_to_nearest(count, 100)
    else:
        return round_to_nearest(count, 1000)


def get_waiting_list_count(*, cache_timeout: int = 300) -> int:
    """
    Get the count of waiting list entries with caching.

    Args:
        cache_timeout: Cache timeout in seconds (default: 5 minutes)

    Returns:
        Number of waiting list entries
    """
    cache_key = "waiting_list_count"

    # Try to get from cache first
    count = cache.get(cache_key)

    if count is None:
        # Cache miss - fetch from database
        count = WaitingList.objects.count()
        # Round the count to the nearest 10
        count = format_waiting_list_count(count)
        # Store in cache with timeout
        cache.set(cache_key, count, cache_timeout)

    return count


def is_user_identity_recently_verified(user: AgoraUser) -> bool:
    """
    Check if the user has a verified identity within the last year.
    """
    return user.identity_verification.filter(
        identity_verification_status=IdentityVerification.IdentityVerificationStatus.VERIFIED,
        created_at__gte=timezone.now() - timezone.timedelta(days=365),
    ).exists()
