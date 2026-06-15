from rest_framework import serializers

from .models import Broadcast, BroadcastRead, CheckIn, InboundMessage, Notification


class CheckInSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()
    hub_name = serializers.SerializerMethodField()

    class Meta:
        model = CheckIn
        fields = [
            "id",
            "user",
            "user_full_name",
            "hub",
            "hub_name",
            "timestamp",
            "people_count",
            "status",
            "road_access",
            "medical_notes",
            "latitude",
            "longitude",
            "channel",
            "client_uuid",
        ]
        read_only_fields = ["id", "timestamp", "user"]

    def get_user_full_name(self, obj):
        return obj.user.full_name if obj.user else None

    def get_hub_name(self, obj):
        return obj.hub.name if obj.hub else None


class CheckInCreateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["safe", "need_assistance"])
    people_count = serializers.IntegerField(default=1)
    road_access = serializers.ChoiceField(choices=["open", "blocked", "unknown"], default="unknown")
    medical_notes = serializers.CharField(required=False, allow_blank=True)
    latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )
    longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )
    client_uuid = serializers.CharField(required=False, allow_null=True)
    hub = serializers.IntegerField()


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
