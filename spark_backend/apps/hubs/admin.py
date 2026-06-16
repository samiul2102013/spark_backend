from django.contrib import admin

from .models import Hub


@admin.register(Hub)
class HubAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "coordinator", "battery_percentage", "starlink_status")
    list_filter = ("status",)
    search_fields = ("name", "address")
