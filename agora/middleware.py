from django.contrib.auth.middleware import RemoteUserMiddleware


class KeycloakRemoteUserMiddleware(RemoteUserMiddleware):
    # https://oauth2-proxy.github.io/oauth2-proxy/configuration/overview#header-options
    header = "X-Forwarded-User"
