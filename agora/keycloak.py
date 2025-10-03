from django.conf import settings
from keycloak import KeycloakAdmin, KeycloakOpenIDConnection

keycloak_connection = KeycloakOpenIDConnection(
    server_url=settings.KEYCLOAK_SERVER_URL,
    username=settings.KEYCLOAK_USERNAME,
    password=settings.KEYCLOAK_PASSWORD,
    realm_name=settings.KEYCLOAK_REALM,
    user_realm_name=settings.KEYCLOAK_USER_REALM,
    verify=settings.KEYCLOAK_VERIFY_CERT,
)

keycloak_admin = KeycloakAdmin(connection=keycloak_connection)
