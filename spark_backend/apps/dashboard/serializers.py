from rest_framework import serializers

from apps.ai.models import SituationReport
from apps.hazards.models import Hazard
from apps.hubs.models import Hub


class HubStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    open = serializers.IntegerField()
    critical = serializers.IntegerField()


class HazardStatsSerializer(serializers.Serializer):
    active = serializers.IntegerField()
    reported_today = serializers.IntegerField()


class BookingStatsSerializer(serializers.Serializer):
    active = serializers.IntegerField()
    today = serializers.IntegerField()


class CheckInStatsSerializer(serializers.Serializer):
    total_today = serializers.IntegerField()
    safe = serializers.IntegerField()
    need_assistance = serializers.IntegerField()


class OverviewSerializer(serializers.Serializer):
    hubs = HubStatsSerializer()
    hazards = HazardStatsSerializer()
    bookings = BookingStatsSerializer()
    checkins = CheckInStatsSerializer()


class HubMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hub
        fields = ["id", "name", "latitude", "longitude", "status", "battery_percentage", "starlink_status"]


class HazardMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hazard
        fields = ["id", "category", "latitude", "longitude", "severity", "status"]


class SituationReportSerializer(serializers.ModelSerializer):
    hub_name = serializers.SerializerMethodField()

    class Meta:
        model = SituationReport
        fields = ["id", "hub", "hub_name", "summary", "generated_by", "is_auto", "created_at", "pdf_file"]

    def get_hub_name(self, obj):
        return obj.hub.name if obj.hub else None


class AlertSerializer(serializers.ModelSerializer):
    hub_name = serializers.SerializerMethodField()
    reporter_name = serializers.SerializerMethodField()

    class Meta:
        model = Hazard
        fields = [
            "id", "category", "severity", "status", "description",
            "latitude", "longitude", "hub_name", "reporter_name", "created_at",
        ]

    def get_hub_name(self, obj):
        return obj.hub.name if obj.hub else None

    def get_reporter_name(self, obj):
        return obj.reporter.full_name if obj.reporter else None


class InfrastructureHubSerializer(serializers.ModelSerializer):
    checkins_today = serializers.SerializerMethodField()
    active_bookings = serializers.SerializerMethodField()

    class Meta:
        model = Hub
        fields = [
            "id", "name", "status", "battery_percentage", "solar_input_w",
            "solar_output_w", "estimated_runtime_h", "starlink_status",
            "max_concurrent_bookings", "latitude", "longitude",
            "checkins_today", "active_bookings",
        ]

    def get_checkins_today(self, obj):
        return getattr(obj, "checkins_today", 0)

    def get_active_bookings(self, obj):
        return getattr(obj, "active_bookings", 0)
