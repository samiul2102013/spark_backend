from rest_framework import serializers

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    hub_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "id",
            "user",
            "user_name",
            "hub",
            "hub_name",
            "start_time",
            "end_time",
            "status",
            "confirmation_sent",
            "check_in_time",
            "device_count",
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

    def get_user_name(self, obj):
        return obj.user.full_name if obj.user else None

    def get_hub_name(self, obj):
        return obj.hub.name if obj.hub else None


class BookingCreateSerializer(serializers.Serializer):
    hub = serializers.IntegerField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField(required=False)
    device_count = serializers.IntegerField(default=1)
    client_uuid = serializers.CharField(required=False, allow_null=True)


class BookingStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["active", "cancelled", "completed"])


class AvailableSlotSerializer(serializers.Serializer):
    start_time = serializers.DateTimeField()
    available = serializers.BooleanField()
