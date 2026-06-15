import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comms", "0002_initial"),
        ("hubs", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Broadcast",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("subject", models.CharField(max_length=255)),
                ("body", models.TextField()),
                (
                    "priority",
                    models.CharField(
                        choices=[("info", "Info"), ("warning", "Warning"), ("urgent", "Urgent")],
                        default="info",
                        max_length=10,
                    ),
                ),
                (
                    "hub",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="broadcasts",
                        to="hubs.hub",
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sent_broadcasts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "broadcasts",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="BroadcastRead",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("read_at", models.DateTimeField(auto_now_add=True)),
                (
                    "broadcast",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reads",
                        to="comms.broadcast",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="broadcast_reads",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "broadcast_reads",
                "unique_together": {("broadcast", "user")},
            },
        ),
        migrations.CreateModel(
            name="CheckIn",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("people_count", models.PositiveIntegerField(default=1)),
                (
                    "status",
                    models.CharField(
                        choices=[("safe", "Safe"), ("need_assistance", "Need Assistance")],
                        default="safe",
                        max_length=20,
                    ),
                ),
                (
                    "road_access",
                    models.CharField(
                        choices=[("open", "Open"), ("blocked", "Blocked"), ("unknown", "Unknown")],
                        default="unknown",
                        max_length=10,
                    ),
                ),
                ("medical_notes", models.TextField(blank=True)),
                (
                    "latitude",
                    models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
                ),
                (
                    "longitude",
                    models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
                ),
                (
                    "channel",
                    models.CharField(
                        choices=[("app", "App"), ("whatsapp", "WhatsApp"), ("sms", "SMS")],
                        default="app",
                        max_length=10,
                    ),
                ),
                (
                    "client_uuid",
                    models.CharField(blank=True, max_length=255, null=True, unique=True),
                ),
                (
                    "hub",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="checkins",
                        to="hubs.hub",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="checkins",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "checkins",
                "ordering": ["-timestamp"],
            },
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("broadcast", "Broadcast"),
                            ("alert", "Alert"),
                            ("booking", "Booking"),
                            ("hub_status", "Hub Status"),
                        ],
                        max_length=15,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("body", models.TextField()),
                ("read", models.BooleanField(default=False)),
                ("link", models.CharField(blank=True, max_length=500, null=True)),
                (
                    "hub",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="notifications",
                        to="hubs.hub",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "notifications",
                "ordering": ["-created_at"],
            },
        ),
    ]
