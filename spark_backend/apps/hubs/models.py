from django.db import models

from core.models import TimeStampedModel


class Hub(TimeStampedModel):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
        ("low_battery", "Low Battery"),
        ("critical", "Critical"),
    ]
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    battery_percentage = models.PositiveIntegerField(default=100)
    solar_input_w = models.IntegerField(null=True, blank=True)
    solar_output_w = models.IntegerField(null=True, blank=True)
    estimated_runtime_h = models.FloatField(null=True, blank=True)
    starlink_status = models.BooleanField(default=True)
    max_concurrent_bookings = models.PositiveIntegerField(default=5)
    total_ports = models.PositiveIntegerField(default=10)
    coordinator = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coordinated_hubs",
    )

    class Meta:
        db_table = "hubs"

    def __str__(self):
        return self.name
