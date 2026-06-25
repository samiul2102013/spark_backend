from rest_framework import serializers

from apps.hazards.models import Comment, Hazard
from apps.hubs.models import Hub


class InfrastructureGovSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    solar = serializers.SerializerMethodField()
    connectivity = serializers.SerializerMethodField()
    sync = serializers.SerializerMethodField()

    class Meta:
        model = Hub
        fields = [
            "id", "name", "location", "status", "battery_percentage",
            "solar", "connectivity", "sync",
        ]

    def get_location(self, obj):
        return {
            "latitude": float(obj.latitude),
            "longitude": float(obj.longitude),
            "address": obj.address,
        }

    def get_status(self, obj):
        return "online" if obj.status == "open" else "offline"

    def get_solar(self, obj):
        return {
            "input_w": obj.solar_input_w,
            "output_w": obj.solar_output_w,
        }

    def get_connectivity(self, obj):
        return {"starlink": obj.starlink_status}

    def get_sync(self, obj):
        return {"last_sync_at": obj.updated_at}


class GovCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "author_name", "body", "photo", "created_at"]

    def get_author_name(self, obj):
        return obj.author.full_name if obj.author else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and data.get("photo"):
            data["photo"] = request.build_absolute_uri(data["photo"])
        return data


class GovHazardDetailSerializer(serializers.ModelSerializer):
    reporter_name = serializers.SerializerMethodField()
    comments = GovCommentSerializer(many=True, read_only=True)
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Hazard
        fields = [
            "id", "category", "severity", "status", "latitude", "longitude",
            "description", "photo", "source", "period", "reporter_name",
            "hub", "created_at", "updated_at", "comments",
        ]

    def get_reporter_name(self, obj):
        return obj.reporter.full_name if obj.reporter else None

    def get_photo(self, obj):
        request = self.context.get("request")
        if request and obj.photo:
            return request.build_absolute_uri(obj.photo.url)
        return None


class OverviewSerializer(serializers.Serializer):
    checkins = serializers.DictField()
    active_hubs = serializers.IntegerField()
    hazard_reports = serializers.IntegerField()
    silent_communications = serializers.IntegerField()
    urgent_flags = serializers.DictField()
    checkins_over_time = serializers.ListField()
    hazard_breakdown = serializers.DictField()


class MapDataSerializer(serializers.Serializer):
    medical_hubs = serializers.DictField()
    hazards = serializers.ListField()
    fall_incidents = serializers.ListField()
    medical_needs = serializers.ListField()


class ReportSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    subtitle = serializers.CharField()
    timestamp = serializers.DateTimeField()
    pdf_url = serializers.URLField()
