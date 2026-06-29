from django.contrib import admin

from .models import AIConfig, SituationReport


@admin.register(SituationReport)
class SituationReportAdmin(admin.ModelAdmin):
    list_display = ("id", "summary", "generated_by", "is_auto", "created_at")
    list_filter = ("generated_by", "is_auto")
    search_fields = ("summary",)


@admin.register(AIConfig)
class AIConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "api_provider", "auto_reporting_enabled", "report_interval_minutes")
