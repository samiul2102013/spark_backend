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
        fields = ["id", "title", "message", "notification_type", "data", "sent_at", "created_at"]
        read_only_fields = ["id", "sent_at", "created_at"]
