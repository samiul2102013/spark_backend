from rest_framework import serializers

from .models import FCMToken, Notification


class FCMTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMToken
        fields = ["id", "token", "platform", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id", "user", "hub", "title", "message", "category",
            "data", "link", "read", "sent_at", "created_at",
        ]
        read_only_fields = ["id", "user", "sent_at", "created_at"]
