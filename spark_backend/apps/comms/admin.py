from django.contrib import admin

from .models import Broadcast, BroadcastRead, CheckIn, InboundMessage, SentMessage


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "hub", "status", "people_count", "timestamp")
    list_filter = ("status",)
    search_fields = ("user__full_name", "hub__name")


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ("id", "hub", "subject", "priority", "sender", "created_at")
    list_filter = ("priority",)
    search_fields = ("subject", "body")


@admin.register(BroadcastRead)
class BroadcastReadAdmin(admin.ModelAdmin):
    list_display = ("broadcast", "user", "read_at")
    search_fields = ("user__full_name",)


@admin.register(InboundMessage)
class InboundMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "from_number", "status", "created_at")
    list_filter = ("source", "status")
    search_fields = ("body", "from_number")


@admin.register(SentMessage)
class SentMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "to_number", "channel", "status", "created_at")
    list_filter = ("channel", "status")
    search_fields = ("to_number", "body")
