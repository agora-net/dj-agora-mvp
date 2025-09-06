from django.contrib import admin

from agora.apps.core.models import WaitingList


@admin.register(WaitingList)
class WaitingListAdmin(admin.ModelAdmin):
    """
    Admin interface for WaitingList model.
    """

    list_display = [
        "email",
        "waiting_list_position",
        "invite_sent_at",
        "invite_accepted_at",
        "created_at",
    ]

    list_filter = [
        "invite_sent_at",
        "invite_accepted_at",
        "created_at",
    ]

    search_fields = [
        "email",
        "invite_code",
    ]

    readonly_fields = [
        "id",
        "invite_code",
        "waiting_list_position",
        "created_at",
        "updated_at",
    ]

    ordering = ["created_at"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "id",
                    "email",
                    "invite_code",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "waiting_list_position",
                    "invite_sent_at",
                    "invite_accepted_at",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )
