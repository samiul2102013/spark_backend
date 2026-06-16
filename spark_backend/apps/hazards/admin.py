from django.contrib import admin

from .models import Comment, Hazard


@admin.register(Hazard)
class HazardAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "severity", "status", "period", "hub", "reporter")
    list_filter = ("category", "severity", "status", "period")
    search_fields = ("description",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "hazard", "author", "created_at")
    search_fields = ("body",)
