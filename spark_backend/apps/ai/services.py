from .models import AIReportingConfig, MessageReviewConfig


class AIConfigService:

    @staticmethod
    def get_message_review_config() -> MessageReviewConfig:
        return MessageReviewConfig.get_solo()

    @staticmethod
    def update_message_review_config(data: dict) -> MessageReviewConfig:
        config = MessageReviewConfig.get_solo()
        for field, value in data.items():
            setattr(config, field, value)
        config.save()
        return config

    @staticmethod
    def get_reporting_config() -> AIReportingConfig:
        return AIReportingConfig.get_solo()

    @staticmethod
    def update_reporting_config(data: dict) -> AIReportingConfig:
        config = AIReportingConfig.get_solo()
        for field, value in data.items():
            setattr(config, field, value)
        config.save()
        return config


class MessageReviewService:

    @staticmethod
    def get_review_queue(status=None, severity=None, source=None) -> list[dict]:
        results = []

        if source is None or source == "hazard":
            from apps.hazards.models import Hazard

            qs = Hazard.objects.exclude(description__isnull=True).exclude(description__exact="")
            if status:
                qs = qs.filter(review_status=status)
            if severity:
                qs = qs.filter(severity=severity)

            for h in qs.select_related("reporter", "hub"):
                results.append(MessageReviewService._shape_hazard(h))

        if source is None or source == "checkin":
            from apps.comms.models import CheckIn

            qs = CheckIn.objects.exclude(
                help_description__isnull=True
            ).exclude(help_description__exact="")
            if status:
                qs = qs.filter(review_status=status)

            for c in qs.select_related("user", "hub"):
                results.append(MessageReviewService._shape_checkin(c))

        results.sort(key=lambda r: r["created_at"], reverse=True)
        return results

    @staticmethod
    def _shape_hazard(h) -> dict:
        return {
            "id": h.id,
            "source": "hazard",
            "message": h.description,
            "hazard_type": h.category,
            "severity": h.severity,
            "risk_score": h.risk_score,
            "review_status": h.review_status,
            "reporter": h.reporter.full_name if h.reporter else None,
            "hub_name": h.hub.name if h.hub else None,
            "latitude": float(h.latitude) if h.latitude else None,
            "longitude": float(h.longitude) if h.longitude else None,
            "photo_url": h.photo.url if h.photo else None,
            "created_at": h.created_at,
        }

    @staticmethod
    def _shape_checkin(c) -> dict:
        return {
            "id": c.id,
            "source": "checkin",
            "message": c.help_description,
            "hazard_type": None,
            "severity": None,
            "risk_score": c.risk_score,
            "review_status": c.review_status,
            "reporter": c.user.full_name if c.user else None,
            "hub_name": c.hub.name if c.hub else None,
            "latitude": float(c.latitude) if c.latitude else None,
            "longitude": float(c.longitude) if c.longitude else None,
            "photo_url": c.photo.url if c.photo else None,
            "created_at": c.created_at,
        }

    @staticmethod
    def get_review_item(source: str, item_id: int) -> dict:
        if source == "hazard":
            from apps.hazards.models import Hazard

            h = Hazard.objects.select_related("reporter", "hub").get(id=item_id)
            return MessageReviewService._shape_hazard(h)
        elif source == "checkin":
            from apps.comms.models import CheckIn

            c = CheckIn.objects.select_related("user", "hub").get(id=item_id)
            return MessageReviewService._shape_checkin(c)
        else:
            raise ValueError(f"Invalid source '{source}'. Must be 'hazard' or 'checkin'.")

    @staticmethod
    def update_review_status(source: str, item_id: int, new_status: str, reviewed_by_user) -> dict:
        from django.utils import timezone

        if source == "hazard":
            from apps.hazards.models import Hazard

            obj = Hazard.objects.get(id=item_id)
        elif source == "checkin":
            from apps.comms.models import CheckIn

            obj = CheckIn.objects.get(id=item_id)
        else:
            raise ValueError(f"Invalid source '{source}'. Must be 'hazard' or 'checkin'.")

        obj.review_status = new_status
        obj.reviewed_by = reviewed_by_user
        obj.reviewed_at = timezone.now()
        obj.save(update_fields=["review_status", "reviewed_by", "reviewed_at"])

        if source == "hazard":
            return MessageReviewService._shape_hazard(obj)
        else:
            return MessageReviewService._shape_checkin(obj)


class AIScoringService:

    @staticmethod
    def assign_risk_score(message: str, category: str = None) -> int | None:
        from django.conf import settings

        config = MessageReviewConfig.get_solo()
        if not config.autonomous_classification:
            return None

        if not message or not message.strip():
            return None

        import logging
        import os

        from groq import Groq

        logger = logging.getLogger(__name__)

        try:
            api_key = os.environ.get("GROQ_API_KEY") or settings.GROQ_API_KEY
            if not api_key:
                logger.warning("GROQ_API_KEY not set — skipping AI risk scoring")
                return None

            model = os.environ.get("GROQ_MODEL", getattr(settings, "GROQ_MODEL", "llama-3.1-8b-instant"))

            groq_kwargs = {"api_key": api_key}
            base_uri = os.environ.get("GROQ_BASE_URI") or getattr(settings, "GROQ_BASE_URI", None)
            if base_uri:
                groq_kwargs["base_url"] = base_uri

            client = Groq(**groq_kwargs)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You score disaster/emergency messages by urgency. "
                            "Reply with ONLY a single digit: 1 (minor), 2 (moderate), "
                            "or 3 (critical/life-threatening). No words, no punctuation, just the digit."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Category: {category or 'general'}. Message: {message}",
                    },
                ],
                max_tokens=5,
                temperature=0,
            )

            raw = response.choices[0].message.content.strip()
            score = int(raw)
            if score not in (1, 2, 3):
                logger.warning("Groq returned unexpected score %s — returning None", raw)
                return None
            return score

        except Exception:
            logger.warning("Groq API call failed for message: %.60s", message, exc_info=True)
            return None


class ReportGenerationService:

    @staticmethod
    def gather_stats(config) -> dict:
        from datetime import timedelta
        from django.utils import timezone
        from apps.hazards.models import Hazard
        from apps.comms.models import CheckIn
        from apps.hubs.models import Hub

        stats = {}

        if config.include_activity_summary:
            stats["activity"] = {
                "total_hazards": Hazard.objects.count(),
                "by_review_status": {
                    s: Hazard.objects.filter(review_status=s).count()
                    for s in ("pending", "reviewed", "escalated", "resolved")
                },
                "checkins_24h": CheckIn.objects.filter(
                    timestamp__gte=timezone.now() - timedelta(hours=24)
                ).count(),
            }

        if config.include_hubs_summary:
            stats["hubs"] = {
                "total": Hub.objects.count(),
                "open": Hub.objects.filter(status="open").count(),
                "low_battery": Hub.objects.filter(battery_percentage__lt=20).count(),
            }

        if config.include_alerts_summary:
            stats["alerts"] = {
                "escalated_hazards": Hazard.objects.filter(review_status="escalated").count(),
                "silent_communities": Hub.objects.filter(
                    checkins__isnull=True
                ).count()  # hubs with no check-ins ever
            }

        if config.include_ai_performance:
            from apps.comms.models import CheckIn

            stats["ai_performance"] = {
                "hazards": {
                    "auto_scored": Hazard.objects.filter(risk_score__isnull=False).count(),
                    "pending_review": Hazard.objects.filter(risk_score__isnull=True).count(),
                },
                "checkins": {
                    "auto_scored": CheckIn.objects.filter(risk_score__isnull=False).count(),
                    "pending_review": CheckIn.objects.filter(risk_score__isnull=True).count(),
                },
            }

        return stats

    @staticmethod
    def build_summary_text(stats: dict) -> str:
        parts = []

        if "activity" in stats:
            a = stats["activity"]
            parts.append(
                f"Activity: {a['total_hazards']} hazards reported "
                f"({a['by_review_status']['escalated']} escalated, "
                f"{a['by_review_status']['resolved']} resolved). "
                f"{a['checkins_24h']} check-ins in the last 24 hours."
            )

        if "hubs" in stats:
            h = stats["hubs"]
            parts.append(
                f"Hubs: {h['open']} active out of {h['total']} total, "
                f"{h['low_battery']} with low battery."
            )

        if "alerts" in stats:
            al = stats["alerts"]
            parts.append(
                f"Alerts: {al['escalated_hazards']} escalated hazards, "
                f"{al['silent_communities']} communities with no check-ins."
            )

        if "ai_performance" in stats:
            ap = stats["ai_performance"]
            parts.append(
                f"AI Performance: {ap['hazards']['auto_scored']} hazards auto-scored, "
                f"{ap['hazards']['pending_review']} pending review; "
                f"{ap['checkins']['auto_scored']} check-ins auto-scored, "
                f"{ap['checkins']['pending_review']} pending review."
            )

        return " ".join(parts)

    @staticmethod
    def generate_pdf(report_id: int, summary: str, stats: dict) -> str:
        import os
        from datetime import datetime
        from django.conf import settings
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch

        reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        filepath = os.path.join(reports_dir, f"report_{report_id}.pdf")

        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 18)
        c.drawString(inch, height - inch, "SPARK Situation Report")

        c.setFont("Helvetica", 10)
        c.drawString(inch, height - 1.4 * inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, height - 2.0 * inch, "Summary")

        c.setFont("Helvetica", 10)
        y = height - 2.5 * inch
        for line in summary.split(". "):
            c.drawString(inch + 10, y, f"  - {line.strip()}.")
            y -= 0.3 * inch
            if y < inch:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - inch

        y -= 0.3 * inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y, "Statistics Breakdown")
        y -= 0.3 * inch
        c.setFont("Helvetica", 10)

        def _write_stat(label, value, indent=1):
            nonlocal y
            c.drawString(inch + 10 * indent, y, f"{label}: {value}")
            y -= 0.25 * inch

        for section_key, section_data in stats.items():
            if isinstance(section_data, dict):
                flat_items = []

                def _flatten(d, prefix=""):
                    for k, v in d.items():
                        label = f"{prefix}{k.replace('_', ' ').title()}"
                        if isinstance(v, dict):
                            _flatten(v, f"{label} > ")
                        else:
                            flat_items.append((label, v))

                _flatten(section_data)
                for label, val in flat_items:
                    if y < inch:
                        c.showPage()
                        c.setFont("Helvetica", 10)
                        y = height - inch
                    _write_stat(label, val)

        c.save()
        return filepath

    @staticmethod
    def create_report(is_auto: bool = False):
        from .models import AIReportingConfig, SituationReport

        config = AIReportingConfig.get_solo()
        if is_auto and not config.auto_reporting_enabled:
            return None

        stats = ReportGenerationService.gather_stats(config)
        summary = ReportGenerationService.build_summary_text(stats)
        report = SituationReport.objects.create(
            summary=summary, generated_by="ai", is_auto=is_auto
        )
        pdf_path = ReportGenerationService.generate_pdf(report.id, summary, stats)
        report.pdf_file = pdf_path
        report.save(update_fields=["pdf_file"])
        return report
