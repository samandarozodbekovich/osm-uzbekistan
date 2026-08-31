from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, PhoneVerification


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('phone_number', 'full_name', 'is_verified', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_verified', 'is_active', 'is_staff')
    search_fields = ('phone_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal', {'fields': ('first_name', 'last_name')}),
        ('Status', {'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'fields': ('phone_number', 'password1', 'password2')}),
    )


@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'is_used', 'attempts', 'expires_at', 'created_at')
    list_filter = ('is_used',)
    search_fields = ('phone_number',)
    readonly_fields = ('created_at',)
