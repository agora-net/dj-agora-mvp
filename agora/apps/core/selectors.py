from django.core.cache import cache

from agora.apps.core.models import WaitingList


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
        # Store in cache with timeout
        cache.set(cache_key, count, cache_timeout)

    return count
