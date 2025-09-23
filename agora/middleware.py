from django.shortcuts import redirect
from django.urls import reverse

from agora.apps.core.selectors import is_user_identity_recently_verified


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

        # Whitelist route name
        allowed_route_names = []

        # Whitelist paths
        allowed_paths = [reverse(name) for name in allowed_route_names] + []

        if request.path not in allowed_paths:
            return redirect("verification_required")

        return response
