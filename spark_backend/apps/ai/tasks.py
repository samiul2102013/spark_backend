import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def check_and_generate_report():
    from datetime import timedelta
    from django.utils import timezone

    from .models import AIReportingConfig, SituationReport
    from .services import ReportGenerationService

    config = AIReportingConfig.get_solo()
    if not config.auto_reporting_enabled:
        logger.info("Auto-reporting disabled — skipping")
        return

    latest = SituationReport.objects.filter(is_auto=True).order_by("-created_at").first()
    if latest:
        elapsed = timezone.now() - latest.created_at
        if elapsed < timedelta(hours=config.frequency_hours()):
            logger.info("Last auto report %s is %s old — skipping", latest.id, elapsed)
            return

    report = ReportGenerationService.create_report(is_auto=True)
    if report:
        logger.info("Auto-generated report %s", report.id)
    else:
        logger.warning("Auto-report generation returned None")
