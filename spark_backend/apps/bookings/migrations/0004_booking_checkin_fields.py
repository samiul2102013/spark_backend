from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0003_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="check_in_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="booking",
            name="people_count",
            field=models.PositiveIntegerField(default=1),
        ),
    ]
