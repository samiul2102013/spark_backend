from rest_framework import serializers

from apps.hazards.models import Hazard


class UrgentFlagSerializer(serializers.ModelSerializer):
    reporter_name = serializers.SerializerMethodField()
    category_label = serializers.SerializerMethodField()
    severity_label = serializers.SerializerMethodField()

    class Meta:
        model = Hazard
        fields = [
            "id",
            "category",
            "category_label",
            "description",
            "latitude",
            "longitude",
            "severity",
            "severity_label",
            "reporter_name",
            "status",
            "review_status",
            "risk_score",
            "photo",
            "created_at",
        ]

    def get_reporter_name(self, obj):
        return obj.reporter.full_name if obj.reporter else None

    def get_category_label(self, obj):
        return obj.get_category_display()

    def get_severity_label(self, obj):
        return dict(Hazard.SEVERITY_CHOICES).get(obj.severity, "")
