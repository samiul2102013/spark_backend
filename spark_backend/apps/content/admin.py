from django.contrib import admin

from .models import StaticContent


@admin.register(StaticContent)
class StaticContentAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "updated_at")
    search_fields = ("slug", "title")
    readonly_fields = ("updated_at",)
