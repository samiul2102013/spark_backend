from rest_framework import serializers

from .models import Hub


class HubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hub
        fields = (
            "id",
            "name",
            "address",
            "latitude",
            "longitude",
            "status",
            "battery_percentage",
            "solar_input_w",
            "solar_output_w",
            "estimated_runtime_h",
            "starlink_status",
            "max_concurrent_bookings",
            "coordinator",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class HubStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Hub.STATUS_CHOICES)
    battery_percentage = serializers.IntegerField(required=False, min_value=0, max_value=100)
    solar_input_w = serializers.IntegerField(required=False, allow_null=True)
    solar_output_w = serializers.IntegerField(required=False, allow_null=True)


class HubCoordinatorSerializer(serializers.Serializer):
    coordinator_id = serializers.CharField(max_length=20)
