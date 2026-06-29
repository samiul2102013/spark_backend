from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers

from .models import Broadcast, BroadcastRead, CheckIn, InboundMessage, Notification


class CheckInSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()
    hub_name = serializers.SerializerMethodField()
    hub_latitude = serializers.SerializerMethodField()
    hub_longitude = serializers.SerializerMethodField()

    class Meta:
        model = CheckIn
        fields = [
            "id",
            "user",
            "user_full_name",
            "hub",
            "hub_name",
            "hub_latitude",
            "hub_longitude",
            "timestamp",
            "people_count",
            "status",
            "road_access",
            "medical_notes",
            "latitude",
            "longitude",
            "channel",
            "client_uuid",
            "assistance_type",
            "additional_hazard",
            "help_description",
            "photo",
        ]
        read_only_fields = ["id", "timestamp", "user"]

    def get_user_full_name(self, obj):
        return obj.user.full_name if obj.user else None

    def get_hub_name(self, obj):
        return obj.hub.name if obj.hub else None

    def get_hub_latitude(self, obj):
        return float(obj.hub.latitude) if obj.hub else None

    def get_hub_longitude(self, obj):
        return float(obj.hub.longitude) if obj.hub else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and data.get("photo"):
            data["photo"] = request.build_absolute_uri(data["photo"])
        return data


class CheckInCreateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=CheckIn.STATUS_CHOICES)
    people_count = serializers.IntegerField(default=1)
    road_access = serializers.ChoiceField(choices=CheckIn.ROAD_CHOICES, default="unknown")
    medical_notes = serializers.CharField(required=False, allow_blank=True)
    latitude = serializers.DecimalField(
        max_digits=19, decimal_places=16, required=False, allow_null=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = serializers.DecimalField(
        max_digits=19, decimal_places=16, required=False, allow_null=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    client_uuid = serializers.CharField(required=False, allow_null=True)
    hub = serializers.IntegerField()
    assistance_type = serializers.ChoiceField(choices=CheckIn.ASSISTANCE_TYPE_CHOICES, required=False, allow_null=True)
    additional_hazard = serializers.ChoiceField(choices=CheckIn.ADDITIONAL_HAZARD_CHOICES, required=False, allow_null=True)
    help_description = serializers.CharField(required=False, allow_blank=True)
    photo = serializers.ImageField(required=False, allow_null=True)


class BroadcastSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Broadcast
        fields = ["id", "hub", "sender", "sender_name", "subject", "body", "priority", "created_at"]
        read_only_fields = ["id", "created_at", "sender"]

    def get_sender_name(self, obj):
        return obj.sender.full_name if obj.sender else None


class BroadcastCreateSerializer(serializers.Serializer):
    subject = serializers.CharField()
    body = serializers.CharField()
    priority = serializers.ChoiceField(choices=["info", "warning", "urgent"], default="info")


class BroadcastReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastRead
        fields = ["id", "broadcast", "user", "read_at"]
        read_only_fields = ["id", "read_at", "user"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "user", "hub", "type", "title", "body", "read", "link", "created_at"]
        read_only_fields = ["id", "created_at", "user"]


class InboundMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InboundMessage
        fields = "__all__"
