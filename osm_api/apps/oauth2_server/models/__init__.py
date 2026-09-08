import secrets


def generate_auth_code():
    """Named function instead of a lambda — Django migrations can't
    serialize lambdas into migration files, but a plain function
    reference (by import path) works fine.

    Kept here in the package __init__ so its import path stays
    ``apps.oauth2_server.models.generate_auth_code`` — the path the
    existing migration already records.
    """
    return secrets.token_urlsafe(48)


from .oauth_client import OAuthClient
from .authorization_code import AuthorizationCode

__all__ = [
    'generate_auth_code',
    'OAuthClient',
    'AuthorizationCode',
]
