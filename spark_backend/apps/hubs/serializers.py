from django.db.models import Sum

from rest_framework import serializers

from apps.bookings.models import Booking

from .models import Hub


class HubSerializer(serializers.ModelSerializer):
    available_ports = serializers.SerializerMethodField()

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
            "total_ports",
            "available_ports",
            "coordinator",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_available_ports(self, obj):
        used = Booking.objects.filter(hub=obj, status="active").aggregate(total=Sum("device_count"))["total"] or 0
        return obj.total_ports - used


class HubListSerializer(serializers.ModelSerializer):
    available_ports = serializers.SerializerMethodField()

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
            "total_ports",
            "available_ports",
        )

    def get_available_ports(self, obj):
        used = Booking.objects.filter(hub=obj, status="active").aggregate(total=Sum("device_count"))["total"] or 0
        return obj.total_ports - used


class HubStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Hub.STATUS_CHOICES)
    battery_percentage = serializers.IntegerField(required=False, min_value=0, max_value=100)
    solar_input_w = serializers.IntegerField(required=False, allow_null=True)
    solar_output_w = serializers.IntegerField(required=False, allow_null=True)


class HubCoordinatorSerializer(serializers.Serializer):
    coordinator_id = serializers.CharField(max_length=20)


class NearestHubSerializer(serializers.ModelSerializer):
    distance_km = serializers.SerializerMethodField()
    available_ports = serializers.SerializerMethodField()

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
            "total_ports",
            "available_ports",
            "distance_km",
        )

    def get_distance_km(self, obj):
        return obj.distance_km

    def get_available_ports(self, obj):
        used = Booking.objects.filter(hub=obj, status="active").aggregate(total=Sum("device_count"))["total"] or 0
        return obj.total_ports - used


class HubReassignSerializer(serializers.Serializer):
    hub_id = serializers.IntegerField()


class HubReassignResponseSerializer(serializers.Serializer):
    user_id = serializers.CharField(source="phone_number")
    phone_number = serializers.CharField()
    full_name = serializers.CharField()
    hub_id = serializers.IntegerField(source="hub.id", allow_null=True)
    hub_name = serializers.SerializerMethodField()

    def get_hub_name(self, obj):
        return obj.hub.name if obj.hub else None


class HubAssignSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)


class HubAssignResponseSerializer(serializers.ModelSerializer):
    distance_km = serializers.FloatField(read_only=True)

    class Meta:
        model = Hub
        fields = (
            "id", "name", "address", "latitude", "longitude",
            "status", "battery_percentage", "distance_km",
        )


class HubSlotSerializer(serializers.Serializer):
    start_time = serializers.CharField()
    end_time = serializers.CharField()
    available = serializers.BooleanField()
    booked = serializers.BooleanField()
    battery_percentage = serializers.IntegerField()


class HubSlotsResponseSerializer(serializers.Serializer):
    hub = HubSerializer()
    slots = HubSlotSerializer(many=True)
