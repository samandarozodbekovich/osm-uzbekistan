from django.contrib import admin

from ..models import OAuthClient


@admin.register(OAuthClient)
class OAuthClientAdmin(admin.ModelAdmin):
    list_display = ["name", "client_id"]
