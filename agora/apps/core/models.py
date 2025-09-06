import uuid6
from django.core.cache import cache
from django.db import models
from typeid import TypeID


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class WaitingList(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    email = models.EmailField(unique=True)
    invite_code = models.CharField(max_length=255, unique=True)
    invite_sent_at = models.DateTimeField(null=True, blank=True)
    invite_accepted_at = models.DateTimeField(null=True, blank=True)

    # https://github.com/jetify-com/typeid
    _type = "waiting_list"
    _cache_timeout = 30  # seconds

    @property
    def type_id(self):
        return TypeID.from_uuid(prefix=self._type, suffix=self.id)

    @property
    def waiting_list_position(self):
        """
        Calculate the position in the waiting list with configured cache timeout.

        Position is based on:
        - People who joined before this person (earlier created_at)
        - Who haven't had their invite accepted yet (invite_accepted_at is null)

        Returns:
            int: The position in the waiting list (1-based)
        """
        # Create a unique cache key for this instance
        cache_key = str(self.type_id)

        # Try to get cached value
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Count people who joined before this person and haven't accepted their invite
        people_ahead = WaitingList.objects.filter(
            created_at__lt=self.created_at,
            invite_accepted_at__isnull=True,
        ).count()

        # Position is 1-based (first person is position 1)
        position = max(1, people_ahead + 1)

        # Cache the result for configured timeout
        cache.set(cache_key, position, timeout=self._cache_timeout)

        return position

    def invalidate_position_cache(self):
        """
        Invalidate the cached waiting list position for this instance.
        Call this when the position might have changed (e.g., when someone accepts an invite).
        """
        cache_key = str(self.type_id)
        cache.delete(cache_key)

    def pre_cache_position(self):
        """
        Pre-cache the waiting list position for this instance.
        Useful when creating a new entry that will be accessed immediately.
        """
        cache_key = str(self.type_id)

        # Count people who joined before this person and haven't accepted their invite
        people_ahead = WaitingList.objects.filter(
            created_at__lt=self.created_at,
            invite_accepted_at__isnull=True,
        ).count()

        # Position is 1-based (first person is position 1)
        position = max(1, people_ahead + 1)

        # Cache the result for configured timeout
        cache.set(cache_key, position, timeout=self._cache_timeout)

        return position

    def save(self, *args, **kwargs):
        """
        Override save to invalidate cache when invite_accepted_at changes.
        """
        # Check if invite_accepted_at is being changed
        if self.pk:
            try:
                old_instance = WaitingList.objects.get(pk=self.pk)
                if old_instance.invite_accepted_at != self.invite_accepted_at:
                    # Invalidate cache for this instance and potentially others
                    self.invalidate_position_cache()
            except WaitingList.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
