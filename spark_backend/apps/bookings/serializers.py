from rest_framework import serializers

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "user",
            "hub",
            "start_time",
            "end_time",
            "status",
            "confirmation_sent",
            "check_in_time",
            "people_count",
            "client_uuid",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "status",
            "confirmation_sent",
            "check_in_time",
        ]
