from rest_framework import serializers

from .models import Broadcast, BroadcastRead, CheckIn, Notification


class CheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckIn
        fields = [
            "id",
            "user",
            "hub",
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


class BroadcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broadcast
        fields = ["id", "hub", "sender", "subject", "body", "priority", "created_at"]
        read_only_fields = ["id", "created_at", "sender"]


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
