import uuid6
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

    def type_id(self):
        return TypeID.from_uuid(prefix=self._type, uuid=self.id)

    @property
    def waiting_list_position(self):
        """
        Calculate the position in the waiting list.

        Position is based on:
        - People who joined before this person (earlier created_at)
        - Who haven't had their invite accepted yet (invite_accepted_at is null)

        Returns:
            int: The position in the waiting list (1-based)
        """
        # Count people who joined before this person and haven't accepted their invite
        people_ahead = WaitingList.objects.filter(
            created_at__lt=self.created_at,
            invite_accepted_at__isnull=True,
        ).count()

        # Position is 1-based (first person is position 1)
        return people_ahead + 1

    def __str__(self):
        return self.email
