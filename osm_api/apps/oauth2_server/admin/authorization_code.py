from django.contrib import admin

from ..models import AuthorizationCode


@admin.register(AuthorizationCode)
class AuthorizationCodeAdmin(admin.ModelAdmin):
    list_display = ["code", "client", "user", "used", "created_at"]
    readonly_fields = ["code", "client", "user", "redirect_uri", "code_challenge", "created_at"]
