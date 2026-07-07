from django.db import models

from core.models import TimeStampedModel


class DeviceToken(TimeStampedModel):
    PLATFORM_CHOICES = [
        ("ios", "iOS"),
        ("android", "Android"),
        ("web", "Web"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="device_tokens",
    )
    token = models.TextField(unique=True)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES, default="android")

    class Meta:
        db_table = "device_tokens"
        verbose_name = "Device Token"
        verbose_name_plural = "Device Tokens"

    def __str__(self):
        return f"{self.user.phone_number} ({self.platform})"
