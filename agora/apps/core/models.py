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

    def __str__(self):
        return self.email
