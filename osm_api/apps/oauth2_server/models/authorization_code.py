from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from . import generate_auth_code
from .oauth_client import OAuthClient


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
