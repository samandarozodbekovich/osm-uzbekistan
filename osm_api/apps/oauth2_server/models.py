import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_auth_code():
    """Named function instead of a lambda — Django migrations can't
    serialize lambdas into migration files, but a plain function
    reference (by import path) works fine."""
    return secrets.token_urlsafe(48)


class OAuthClient(models.Model):
    client_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    redirect_uris = models.TextField(
        help_text="One redirect URI per line. Must match exactly what the client sends."
    )

    def __str__(self):
        return f"{self.name} ({self.client_id})"

    def allows_redirect_uri(self, uri: str) -> bool:
        allowed = {line.strip() for line in self.redirect_uris.splitlines() if line.strip()}
        return uri in allowed


class AuthorizationCode(models.Model):
    code = models.CharField(max_length=128, unique=True, default=generate_auth_code)
    client = models.ForeignKey(OAuthClient, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    redirect_uri = models.CharField(max_length=500)

    code_challenge = models.CharField(max_length=200)
    code_challenge_method = models.CharField(max_length=10, default="S256")

    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_expired(self) -> bool:
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"code for {self.user} / {self.client.client_id}"