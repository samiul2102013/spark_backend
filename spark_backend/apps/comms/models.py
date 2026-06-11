from django.db import models
from core.models import TimeStampedModel


class InboundMessage(TimeStampedModel):
    SOURCE_CHOICES = [("whatsapp", "WhatsApp"), ("sms", "SMS")]
    STATUS_CHOICES = [("pending", "Pending"), ("classified", "Classified"), ("unclassified", "Unclassified")]
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    from_number = models.CharField(max_length=20)
    body = models.TextField()
    media_url = models.URLField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    classified_hazard = models.ForeignKey(
        "hazards.Hazard", on_delete=models.SET_NULL, null=True, blank=True
    )
    raw_payload = models.JSONField(default=dict)

    class Meta:
        db_table = "inbound_messages"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.source}] {self.from_number}: {self.body[:60]}"


class SentMessage(TimeStampedModel):
    CHANNEL_CHOICES = [("whatsapp", "WhatsApp"), ("sms", "SMS")]
    to_number = models.CharField(max_length=20)
    body = models.TextField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    status = models.CharField(max_length=20, default="pending")
    external_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "sent_messages"

    def __str__(self):
        return f"[{self.channel}] → {self.to_number}: {self.body[:60]}"
