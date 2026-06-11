from django.db import models
from core.models import TimeStampedModel


class SyncLog(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("synced", "Synced"),
        ("conflict", "Conflict"),
        ("error", "Error"),
    ]
    device_id = models.CharField(max_length=255)
    model_name = models.CharField(max_length=100)
    action = models.CharField(max_length=20)
    payload = models.JSONField()
    client_uuid = models.CharField(max_length=255)
    client_timestamp = models.DateTimeField()
    server_timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = "sync_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["device_id", "status"]),
            models.Index(fields=["client_uuid"]),
        ]

    def __str__(self):
        return f"{self.model_name}/{self.action} - {self.status}"
