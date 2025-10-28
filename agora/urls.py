from django.conf import settings
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from agora.apps.core import api_v1, webhooks_v1
from agora.apps.core.views import (
    current_user_profile,
    custom_404,
    dashboard,
    donate,
    home,
    invite,
    login,
    onboarding,
    onboarding_edit_profile,
    signup,
    signup_status,
    user_profile,
    verify_identity,
)

urlpatterns = [
    path("", home, name="home"),
    path("auth/login/", login, name="login"),
    path("signup/", signup, name="signup"),
    path("signup/<uuid:signup_id>/", signup_status, name="signup_status"),
    path("invite/", invite, name="invite"),
    path("donate/", donate, name="donate"),
    path(
        "donate/success/",
        TemplateView.as_view(template_name="core/donate_success.html"),
        name="donate_success",
    ),
    path("onboarding/", onboarding, name="onboarding"),  # Auto redirects to next onboarding step
    path(
        "onboarding/verify/identity", verify_identity, name="verify_identity"
    ),  # Identity verification step
    path(
        "onboarding/profile", onboarding_edit_profile, name="onboarding_profile"
    ),  # Profile completion step
    path("dashboard/", dashboard, name="dashboard"),
    path("profile/", current_user_profile, name="current_user_profile"),
    path("profile/<str:handle>/", user_profile, name="user_profile"),
    path("404/", custom_404, name="404"),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("admin/", admin.site.urls),
    path("api/v1/", api_v1.api.urls),
    path("webhooks/v1/", webhooks_v1.webhooks.urls),
]

if not settings.TESTING:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns = [
        *urlpatterns,
    ] + debug_toolbar_urls()

# Needs to be last to fall back to flatpages
urlpatterns += [
    re_path(r"^(?P<url>.*/)$", views.flatpage),
]
