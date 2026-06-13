from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("phone_number","username", "full_name", "role", "hub", "is_active", "is_invite_accepted")
    list_filter = ("role", "is_active", "is_invite_accepted")
    search_fields = ("phone_number", "full_name", "email")
    ordering = ("phone_number",)
    fieldsets = (
        (None, {"fields": ("phone_number", "username", "password")}),
        (
            "Personal info",
            {"fields": ("full_name", "email", "role", "household_size", "medical_needs")},
        ),
        (
            "Location",
            {"fields": ("hub", "secondary_hub", "latitude", "longitude")},
        ),
        (
            "Auth",
            {"fields": ("biometric_key", "is_invite_accepted")},
        ),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "full_name", "email", "password1", "password2", "role"),
            },
        ),
    )
