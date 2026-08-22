from django.db import models

from core.models import TimeStampedModel


class SituationReport(TimeStampedModel):
    summary = models.TextField()
    extraction = models.JSONField(null=True, blank=True)
    hazard_classification = models.JSONField(null=True, blank=True)
    triage = models.JSONField(null=True, blank=True)
    context_snapshot = models.JSONField(null=True, blank=True)
    report_period_start = models.DateTimeField(null=True, blank=True)
    report_period_end = models.DateTimeField(null=True, blank=True)
    generated_by = models.CharField(max_length=20, default="ai")
    pdf_file = models.FileField(upload_to="reports/", null=True, blank=True)
    is_auto = models.BooleanField(default=True)

    class Meta:
        db_table = "situation_reports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report {self.id} - {self.created_at.date()}"


class AIConfig(TimeStampedModel):
    confidence_threshold = models.FloatField(default=0.7)
    auto_reporting_enabled = models.BooleanField(default=True)
    report_interval_minutes = models.PositiveIntegerField(default=60)
    api_provider = models.CharField(max_length=20, default="openai")
    api_key_encrypted = models.TextField(blank=True)

    class Meta:
        db_table = "ai_config"
        verbose_name = "AI Configuration"


class MessageReviewConfig(models.Model):
    REVIEW_FREQUENCIES = [
        ("60min", "60 Minutes"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
    ]

    confidence_threshold = models.IntegerField(default=70)
    autonomous_classification = models.BooleanField(default=True)
    review_report_frequency = models.CharField(
        max_length=10, choices=REVIEW_FREQUENCIES, default="60min"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "message_review_config"
        verbose_name = "Message Review Configuration"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Message Review Config"


class AIReportingConfig(models.Model):
    auto_reporting_enabled = models.BooleanField(default=True)
    frequency_interval_minutes = models.PositiveIntegerField(default=60)
    include_activity_summary = models.BooleanField(default=True)
    include_hubs_summary = models.BooleanField(default=True)
    include_alerts_summary = models.BooleanField(default=True)
    include_ai_performance = models.BooleanField(default=False)
    use_ai_summary = models.BooleanField(default=False)
    structured_reporting = models.BooleanField(default=True)
    include_extraction = models.BooleanField(default=True)
    include_classification = models.BooleanField(default=True)
    include_triage = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_reporting_config"
        verbose_name = "AI Reporting Configuration"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "AI Reporting Config"
