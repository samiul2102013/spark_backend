from rest_framework import serializers

from .models import Comment, Hazard


class HazardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hazard
        fields = [
            "id",
            "category",
            "description",
            "photo",
            "latitude",
            "longitude",
            "severity",
            "source",
            "status",
            "period",
            "reporter",
            "hub",
            "client_uuid",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "reporter"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "hazard", "author", "body", "photo", "created_at"]
        read_only_fields = ["id", "created_at", "author"]
