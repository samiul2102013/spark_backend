from rest_framework import serializers

from .models import Comment, Hazard


class HazardSerializer(serializers.ModelSerializer):
    reporter_name = serializers.SerializerMethodField()

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
            "reporter_name",
            "hub",
            "client_uuid",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "reporter"]

    def get_reporter_name(self, obj):
        return obj.reporter.full_name if obj.reporter else None


class HazardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hazard
        fields = ["id", "category", "severity", "status", "latitude", "longitude", "created_at"]


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "hazard", "author", "author_name", "body", "photo", "created_at"]
        read_only_fields = ["id", "hazard", "created_at", "author"]

    def get_author_name(self, obj):
        return obj.author.full_name if obj.author else None
