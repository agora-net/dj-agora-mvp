from django.conf import settings
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path, re_path

from agora.apps.core import api_v1, webhooks_v1
from agora.apps.core.views import (
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
    verify_identity,
)

urlpatterns = [
    path("", home, name="home"),
    path("auth/login/", login, name="login"),
    path("signup/", signup, name="signup"),
    path("signup/<uuid:signup_id>/", signup_status, name="signup_status"),
    path("invite/", invite, name="invite"),
    path("donate/", donate, name="donate"),
    path("onboarding/", onboarding, name="onboarding"),  # Auto redirects to next onboarding step
    path(
        "onboarding/verify/identity", verify_identity, name="verify_identity"
    ),  # Identity verification step
    path(
        "onboarding/profile", onboarding_edit_profile, name="onboarding_profile"
    ),  # Profile completion step
    path("dashboard/", dashboard, name="dashboard"),
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
