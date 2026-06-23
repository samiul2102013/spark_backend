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


class HubListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hub
        fields = (
            "id",
            "name",
            "address",
            "status",
            "battery_percentage",
            "latitude",
            "longitude",
            "starlink_status",
        )


class HubStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Hub.STATUS_CHOICES)
    battery_percentage = serializers.IntegerField(required=False, min_value=0, max_value=100)
    solar_input_w = serializers.IntegerField(required=False, allow_null=True)
    solar_output_w = serializers.IntegerField(required=False, allow_null=True)


class HubCoordinatorSerializer(serializers.Serializer):
    coordinator_id = serializers.CharField(max_length=20)


class NearestHubSerializer(serializers.ModelSerializer):
    distance_km = serializers.SerializerMethodField()

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
            "starlink_status",
            "max_concurrent_bookings",
            "distance_km",
        )

    def get_distance_km(self, obj):
        return obj.distance_km


class HubSlotSerializer(serializers.Serializer):
    start_time = serializers.CharField()
    end_time = serializers.CharField()
    available = serializers.BooleanField()
    booked = serializers.BooleanField()
    battery_percentage = serializers.IntegerField()


class HubSlotsResponseSerializer(serializers.Serializer):
    hub = HubSerializer()
    slots = HubSlotSerializer(many=True)
