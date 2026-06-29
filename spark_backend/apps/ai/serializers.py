from rest_framework import serializers

from .models import AIReportingConfig, MessageReviewConfig, SituationReport


class MessageReviewConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageReviewConfig
        fields = [
            "confidence_threshold",
            "autonomous_classification",
            "review_report_frequency",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]

    def validate_confidence_threshold(self, value):
        if value < 1 or value > 100:
            raise serializers.ValidationError(
                "confidence_threshold must be between 1 and 100."
            )
        return value


class AIReportingConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIReportingConfig
        fields = [
            "auto_reporting_enabled",
            "frequency",
            "include_activity_summary",
            "include_hubs_summary",
            "include_alerts_summary",
            "include_ai_performance",
            "use_ai_summary",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]


class MessageReviewItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    source = serializers.CharField()
    message = serializers.CharField()
    hazard_type = serializers.CharField(allow_null=True)
    severity = serializers.IntegerField(allow_null=True)
    risk_score = serializers.IntegerField(allow_null=True)
    review_status = serializers.CharField()
    reporter = serializers.CharField(allow_null=True)
    hub_name = serializers.CharField(allow_null=True)
    latitude = serializers.FloatField(allow_null=True)
    longitude = serializers.FloatField(allow_null=True)
    photo_url = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()


class MessageReviewStatusUpdateSerializer(serializers.Serializer):
    review_status = serializers.ChoiceField(
        choices=["pending", "reviewed", "escalated", "resolved"]
    )


class SituationReportSerializer(serializers.ModelSerializer):
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = SituationReport
        fields = [
            "id",
            "summary",
            "generated_by",
            "is_auto",
            "pdf_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_pdf_url(self, obj):
        request = self.context.get("request")
        if request and obj.pdf_file:
            return request.build_absolute_uri(obj.pdf_file.url)
        return None
