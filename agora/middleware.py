import structlog
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from agora.apps.core.selectors import is_user_identity_recently_verified

from .selectors import is_named_url

logger = structlog.get_logger(__name__)


class VerificationRequiredMiddleware:
    """
    Middleware to ensure that the user has a verified identity.

    Will only check for verified identity if the user is authenticated, otherwise we assume
    that no identity verification is required.

    To whitelist routes that require authentication but not identity verification,
    add the route name or path to the allowed_route_names or allowed_paths list.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # First, ensure the user is logged in. If not, the middleware does nothing.
        if not request.user.is_authenticated:
            return response

        # If the user is already verified, the middleware's job is done.
        if is_user_identity_recently_verified(request.user):
            return response

        verify_identity_url_name_path = getattr(settings, "VERIFY_IDENTITY_URL", "verify_identity")
        if is_named_url(verify_identity_url_name_path):
            verify_identity_url_name_path = reverse(verify_identity_url_name_path)

        # Whitelist route name
        allowed_route_names = ["invite", "home"]

        # Whitelist paths
        allowed_paths = [reverse(name) for name in allowed_route_names] + [
            verify_identity_url_name_path,
            "/favicon.ico",
        ]

        allowed_paths_startswith = [
            "/static/",
            "/media/",
            "/admin/",
            "/oidc/",
            "/__debug__/",
            "/onboarding/",
            "/signup/",
        ]

        starts_with_allowed_path = any(
            request.path.startswith(path) for path in allowed_paths_startswith
        )

        if request.path not in allowed_paths and not starts_with_allowed_path:
            logger.info(
                "User is not verified, redirecting to verification page",
                user_id=request.user.id,
                verify_identity_url_name_path=verify_identity_url_name_path,
            )

            return redirect(verify_identity_url_name_path)

        return response
