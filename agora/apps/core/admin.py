from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from .models import AgoraUser, WaitingList


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


@admin.register(AgoraUser)
class AgoraUserAdmin(auth_admin.UserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("name",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["email", "name", "is_superuser"]
    search_fields = ["name"]
    ordering = ["id"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
