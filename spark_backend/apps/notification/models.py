from django.db import models

from core.models import TimeStampedModel


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="notification_preference",
        primary_key=True,
    )
    push_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_preferences"

    def __str__(self):
        return f"Preferences for {self.user.phone_number}"


class FCMToken(TimeStampedModel):
    PLATFORM_CHOICES = [
        ("ios", "iOS"),
        ("android", "Android"),
        ("web", "Web"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="fcm_tokens",
    )
    token = models.TextField(unique=True)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES, default="android")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "fcm_tokens"
        verbose_name = "FCM Token"
        verbose_name_plural = "FCM Tokens"

    def __str__(self):
        return f"{self.user.phone_number} ({self.platform})"


class ScheduledNotification(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_types = models.JSONField(default=list)
    data = models.JSONField(default=dict, blank=True)
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    target_hub = models.ForeignKey(
        "hubs.Hub", on_delete=models.SET_NULL, null=True, blank=True
    )
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "scheduled_notifications"

    def __str__(self):
        return f"[{self.status}] {self.title}"

    def get_target_users(self):
        if self.target_hub:
            return self.target_hub.residents.all()
        from django.contrib.auth import get_user_model
        return get_user_model().objects.all()


class Notification(TimeStampedModel):
    CATEGORY_CHOICES = [
        ("broadcast", "Broadcast"),
        ("alert", "Alert"),
        ("booking", "Booking"),
        ("hub_status", "Hub Status"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="push_notifications",
    )
    hub = models.ForeignKey(
        "hubs.Hub", on_delete=models.SET_NULL, null=True, blank=True, related_name="notification_records"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default="alert")
    data = models.JSONField(default=dict, blank=True)
    link = models.CharField(max_length=500, null=True, blank=True)
    read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    scheduled_notification = models.ForeignKey(
        "ScheduledNotification",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )

    class Meta:
        db_table = "notification_records"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.category}] {self.title} -> {self.user.phone_number}"
