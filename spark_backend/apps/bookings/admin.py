from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "hub", "status", "start_time", "end_time", "device_count")
    list_filter = ("status",)
    search_fields = ("user__full_name", "hub__name")
