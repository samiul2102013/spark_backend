from django.contrib import admin

from .models import FCMToken, Notification, NotificationPreference, ScheduledNotification


@admin.register(FCMToken)
class FCMTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "platform", "is_active", "created_at"]
    list_filter = ["platform", "is_active"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "category", "read", "sent_at", "created_at"]
    list_filter = ["category", "read"]


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ["user", "push_enabled", "email_enabled", "in_app_enabled"]


@admin.register(ScheduledNotification)
class ScheduledNotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "scheduled_at", "sent_count", "failed_count"]
    list_filter = ["status"]
