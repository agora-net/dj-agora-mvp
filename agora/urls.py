from django.conf import settings
from django.contrib import admin
from django.urls import path

from agora.apps.core.views import custom_404, home, signup, signup_status

urlpatterns = [
    path("", home, name="home"),
    path("signup/", signup, name="signup"),
    path("signup/<uuid:signup_id>/", signup_status, name="signup_status"),
    path("404/", custom_404, name="404"),
    path("admin/", admin.site.urls),
]

if not settings.TESTING:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns = [
        *urlpatterns,
    ] + debug_toolbar_urls()
