from django.db import models

from core.models import TimeStampedModel


class Comment(TimeStampedModel):
    hazard = models.ForeignKey("hazards.Hazard", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hazard_comments",
    )
    body = models.TextField()
    photo = models.ImageField(upload_to="comments/", null=True, blank=True)

    class Meta:
        db_table = "comments"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.hazard}"


class Hazard(TimeStampedModel):
    CATEGORY_CHOICES = [
        ("flooding", "Flood"),
        ("fallen_tree", "Fallen Tree"),
        ("blocked_road", "Blocked Road"),
        ("fallen_utility_pole", "Fallen Utility Pole"),
        ("medical", "Urgent Medical"),
        ("fire", "Fire"),
        ("collapsed_building", "Collapsed Building"),
        ("power_line_down", "Power Line Down"),
        ("landslide", "Landslide"),
        ("earthquake", "Earthquake"),
        ("storm", "Storm"),
        ("other", "Other"),
    ]
    SEVERITY_CHOICES = [(1, "Low"), (2, "Medium"), (3, "High")]
    SOURCE_CHOICES = [
        ("app", "App"),
        ("whatsapp", "WhatsApp"),
        ("sms", "SMS"),
        ("ai", "AI"),
    ]
    STATUS_CHOICES = [("active", "Active"), ("cleared", "Cleared")]
    PERIOD_CHOICES = [("pre", "Pre-Disaster"), ("post", "Post-Disaster")]

    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField()
    photo = models.ImageField(upload_to="hazards/", null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    severity = models.PositiveSmallIntegerField(choices=SEVERITY_CHOICES, default=1)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="app")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default="post")
    reporter = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_hazards",
    )
    hub = models.ForeignKey(
        "hubs.Hub", on_delete=models.CASCADE, null=True, blank=True, related_name="hazards"
    )
    client_uuid = models.CharField(max_length=255, unique=True, null=True, blank=True)
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
        related_name="reviewed_hazards",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "hazards"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_category_display()} - {self.status}"
