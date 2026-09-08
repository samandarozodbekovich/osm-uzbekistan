from django.db import models


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
