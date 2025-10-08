import structlog
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import path, reverse
from django.urls.resolvers import URLPattern
from django.utils.translation import gettext_lazy as _

from .models import AgoraUser, IdentityVerification, WaitingList
from .services import send_waiting_list_invite_email

logger = structlog.get_logger(__name__)


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

    def get_urls(self) -> list[URLPattern]:
        urls = super().get_urls()
        custom_urls = [
            path(
                "<str:object_id>/send_invite/",
                self.admin_site.admin_view(self.send_invite_view),
                name="waitinglist_send_invite",
            ),
        ]
        return custom_urls + urls

    def send_invite_view(self, request: HttpRequest, object_id: str) -> HttpResponse:
        logger.info("sending invite", object_id=object_id)

        waiting_list_entry = self.model.objects.get(pk=object_id)

        send_waiting_list_invite_email(
            email=waiting_list_entry.email,
            waiting_list_entry=waiting_list_entry,
            invite_url=request.build_absolute_uri(
                reverse("invite")
                + f"?email={waiting_list_entry.email}&invite_code={waiting_list_entry.invite_code}"
            ),
        )
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", ".."))

    def change_view(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        request: HttpRequest,
        object_id: str,
        form_url: str = "",
        extra_context: dict[str, str] | None = None,
    ) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context["send_invite_url"] = f"{object_id}/send_invite/"
        return super().change_view(request, object_id, form_url, extra_context)  # pyright: ignore[reportArgumentType]


@admin.register(AgoraUser)
class AgoraUserAdmin(auth_admin.UserAdmin):
    readonly_fields = ["id", "last_login", "date_joined", "keycloak_id", "email"]

    fieldsets = (
        (None, {"fields": ("email", "password", "handle", "keycloak_id")}),
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
    list_display = ["email", "name", "handle", "keycloak_id", "is_superuser"]
    search_fields = ["name", "keycloak_id", "handle", "email"]
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


@admin.register(IdentityVerification)  # Added registration for IdentityVerification
class IdentityVerificationAdmin(admin.ModelAdmin):
    """
    Admin interface for IdentityVerification model.
    """

    list_display = [
        "user",
        "service",
        "status",
        "external_id",
        "created_at",
    ]
    list_filter = [
        "service",
        "status",
        "created_at",
    ]
    search_fields = [
        "user__email",
        "external_id",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at"]
