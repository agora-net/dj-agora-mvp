import structlog
from django.contrib.auth.models import Group
from django.db import transaction
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

logger = structlog.get_logger(__name__)


class AgoraOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    """
    Taking inspiration from:
    - https://mozilla-django-oidc.readthedocs.io/en/stable/installation.html#connecting-oidc-user-identities-to-django-users
    - https://github.com/Amsterdam/keycloak_oidc/blob/master/keycloak_oidc/auth.py
    """

    def create_user(self, claims):
        logger.info("Creating new user from OIDC claims", claims=claims)
        email = claims.get("email")
        name = claims.get("name", "")  # Name is optional so default to empty string
        keycloak_id = claims.get("sub")

        user = self.UserModel.objects.create_user(email=email, name=name, keycloak_id=keycloak_id)  # pyright: ignore[reportCallIssue]

        self.update_groups(user, claims)

        return user

    def update_user(self, user, claims):
        user.name = claims.get("name", "")
        user.save()
        self.update_groups(user, claims)

        return user

    def update_groups(self, user, claims):
        """
        Transform roles obtained from keycloak into Django Groups and
        add them to the user. Note that any role not passed via keycloak
        will be removed from the user.
        """
        with transaction.atomic():
            user.groups.clear()
            for role in claims.get("roles"):
                group, _ = Group.objects.get_or_create(name=role)
                group.user_set.add(user)

    def get_userinfo(self, access_token, id_token, payload):
        """
        Get user details from the access_token and id_token and return
        them in a dict.
        """
        userinfo = super().get_userinfo(access_token, id_token, payload)
        accessinfo = self.verify_token(access_token, nonce=payload.get("nonce"))
        roles = accessinfo.get("realm_access", {}).get("roles", [])

        userinfo["roles"] = roles
        return userinfo
