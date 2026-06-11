from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("phone_number", "full_name", "role", "hub", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("phone_number", "full_name")
    ordering = ("phone_number",)
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (
            "Personal info",
            {"fields": ("full_name", "email", "role", "household_size", "medical_needs")},
        ),
        ("Hub", {"fields": ("hub", "community_secret_code")}),
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
                "fields": ("phone_number", "full_name", "password1", "password2", "role"),
            },
        ),
    )
