from django.db import models
from core.models import TimeStampedModel


class SituationReport(TimeStampedModel):
    hub = models.ForeignKey("hubs.Hub", on_delete=models.CASCADE, null=True, blank=True, related_name="reports")
    summary = models.TextField()
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
