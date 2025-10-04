from django.conf import settings
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path, re_path

from agora.apps.core.views import custom_404, dashboard, home, invite, login, signup, signup_status

urlpatterns = [
    path("", home, name="home"),
    path("auth/login/", login, name="login"),
    path("signup/", signup, name="signup"),
    path("signup/<uuid:signup_id>/", signup_status, name="signup_status"),
    path("invite/", invite, name="invite"),
    path(
        "onboarding/verify/identity", custom_404, name="verify_identity"
    ),  # Placeholder for future identity verification route
    path("dashboard/", dashboard, name="dashboard"),
    path("404/", custom_404, name="404"),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("admin/", admin.site.urls),
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
