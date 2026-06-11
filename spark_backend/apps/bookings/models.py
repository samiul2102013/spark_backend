from django.db import models
from core.models import TimeStampedModel


class Booking(TimeStampedModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="bookings")
    hub = models.ForeignKey("hubs.Hub", on_delete=models.CASCADE, related_name="bookings")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    confirmation_sent = models.BooleanField(default=False)
    client_uuid = models.CharField(max_length=255, unique=True, null=True, blank=True)

    class Meta:
        db_table = "bookings"
        ordering = ["-start_time"]

    def __str__(self):
        return f"{self.user.full_name} @ {self.hub.name} ({self.start_time})"
