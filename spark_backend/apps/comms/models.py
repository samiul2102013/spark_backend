from django.db import models

from core.models import TimeStampedModel


class InboundMessage(TimeStampedModel):
    SOURCE_CHOICES = [("whatsapp", "WhatsApp"), ("sms", "SMS")]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("classified", "Classified"),
        ("unclassified", "Unclassified"),
    ]
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


class CheckIn(TimeStampedModel):
    STATUS_CHOICES = [("safe", "Safe"), ("need_assistance", "Need Assistance")]
    ROAD_CHOICES = [("open", "Open"), ("blocked", "Blocked"), ("unknown", "Unknown")]
    CHANNEL_CHOICES = [("app", "App"), ("whatsapp", "WhatsApp"), ("sms", "SMS")]
    ASSISTANCE_TYPE_CHOICES = [
        ("medical", "Medical"),
        ("trapped", "Trapped"),
        ("need_supplies", "Need Supplies"),
        ("unsafe_building", "Unsafe Area"),
        ("fallen_tree", "Fallen Tree"),
        ("utility_pole", "Damaged Utility Pole"),
        ("security_concern", "Security Concern"),
        ("vehicle_breakdown", "Vehicle Breakdown"),
        ("stranded", "Stranded"),
    ]
    ADDITIONAL_HAZARD_CHOICES = [
        ("collapsed_building", "Collapsed Building"),
        ("landslide", "Landslide"),
        ("power_line_down", "Power Line Down"),
        ("other", "Other"),
        ("lost_or_separated", "Lost or Separated"),
        ("mental_health_crisis", "Mental Health Crisis"),
        ("fire", "Fire"),
    ]

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="checkins")
    hub = models.ForeignKey("hubs.Hub", on_delete=models.CASCADE, related_name="checkins")
    timestamp = models.DateTimeField(auto_now_add=True)
    people_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="safe")
    road_access = models.CharField(max_length=10, choices=ROAD_CHOICES, default="unknown")
    medical_notes = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=19, decimal_places=16, null=True, blank=True)
    longitude = models.DecimalField(max_digits=19, decimal_places=16, null=True, blank=True)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default="app")
    client_uuid = models.CharField(max_length=255, unique=True, null=True, blank=True)
    assistance_type = models.CharField(max_length=30, choices=ASSISTANCE_TYPE_CHOICES, null=True, blank=True)
    additional_hazard = models.CharField(max_length=30, choices=ADDITIONAL_HAZARD_CHOICES, null=True, blank=True)
    help_description = models.TextField(blank=True)
    photo = models.ImageField(upload_to="checkins/", null=True, blank=True)
    risk_score = models.IntegerField(null=True, blank=True)
    review_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("reviewed", "Reviewed"),
            ("escalated", "Escalated"),
            ("resolved", "Resolved"),
        ],
        default="pending",
    )
    reviewed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_checkins",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "checkins"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} @ {self.hub} — {self.status}"


class Broadcast(TimeStampedModel):
    PRIORITY_CHOICES = [("info", "Info"), ("warning", "Warning"), ("urgent", "Urgent")]

    hub = models.ForeignKey("hubs.Hub", on_delete=models.CASCADE, related_name="broadcasts")
    sender = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_broadcasts",
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="info")

    class Meta:
        db_table = "broadcasts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.priority}] {self.subject}"


class BroadcastRead(TimeStampedModel):
    broadcast = models.ForeignKey("comms.Broadcast", on_delete=models.CASCADE, related_name="reads")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="broadcast_reads")
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "broadcast_reads"
        unique_together = [("broadcast", "user")]

    def __str__(self):
        return f"{self.user} read {self.broadcast}"


class Notification(TimeStampedModel):
    TYPE_CHOICES = [
        ("broadcast", "Broadcast"),
        ("alert", "Alert"),
        ("booking", "Booking"),
        ("hub_status", "Hub Status"),
    ]

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="notifications")
    hub = models.ForeignKey(
        "hubs.Hub", on_delete=models.SET_NULL, null=True, blank=True, related_name="notifications"
    )
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    body = models.TextField()
    read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}"
