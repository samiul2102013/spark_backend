from .models import AIReportingConfig, MessageReviewConfig


SPARK_SYSTEM_PROMPT = (
    "You are a disaster response reporting assistant for SPARK (Strategic Platform for "
    "Automated Response and Knowledge). Generate concise situation reports for government officials.\n\n"
    "RULES:\n"
    "- Use ONLY the numbers provided — never invent data\n"
    "- Write 2-3 sentences maximum\n"
    "- Be specific with counts and percentages\n"
    "- Use professional, factual language\n"
    "- Do NOT use markdown, headers, bullet points, or prefixes\n"
    "- Do NOT add commentary, recommendations, or opinions\n"
    "- Each section (Activity, Hubs, Alerts, AI Performance) gets exactly one sentence if its data is provided\n\n"
    "OUTPUT FORMAT:\n"
    "A single paragraph of 2-3 sentences covering all provided sections."
)


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

        from anthropic import Anthropic

        logger = logging.getLogger(__name__)

        try:
            api_key = settings.CLAUDE_API_KEY
            if not api_key:
                logger.warning("CLAUDE_API_KEY not set — skipping AI risk scoring")
                return None

            model = settings.CLAUDE_MODEL

            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model=model,
                max_tokens=10,
                temperature=0,
                system=[
                    {
                        "type": "text",
                        "text": (
                            "You score disaster/emergency messages by urgency. "
                            "Reply with ONLY a single digit: 1 (minor), 2 (moderate), "
                            "or 3 (critical/life-threatening). No words, no punctuation, just the digit."
                        ),
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": f"Category: {category or 'general'}. Message: {message}",
                    },
                ],
            )

            raw = response.content[0].text.strip()
            score = int(raw)
            if score not in (1, 2, 3):
                logger.warning("Claude returned unexpected score %s — returning None", raw)
                return None
            return score

        except Exception:
            logger.warning("Claude API call failed for message: %.60s", message, exc_info=True)
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

        from reportlab.lib.utils import simpleSplit

        c.setFont("Helvetica", 10)
        max_width = width - 2 * inch
        y = height - 2.5 * inch
        for line in simpleSplit(summary, "Helvetica", 10, max_width):
            c.drawString(inch + 10, y, line)
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

        from reportlab.lib.utils import simpleSplit as _split

        def _write_stat(label, value, indent=1):
            nonlocal y
            line = f"{label}: {value}"
            for wrapped in _split(line, "Helvetica", 10, width - 2 * inch):
                c.drawString(inch + 10 * indent, y, wrapped)
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
    def generate_ai_summary(stats: dict, config) -> str | None:
        import hashlib
        import json
        import logging

        from django.conf import settings
        from django.core.cache import cache
        from anthropic import Anthropic

        logger = logging.getLogger(__name__)

        if not settings.CLAUDE_API_KEY:
            logger.warning("CLAUDE_API_KEY not set — cannot generate AI summary")
            return None

        cache_key = "ai_report_summary_" + hashlib.md5(json.dumps(stats, sort_keys=True).encode()).hexdigest()
        cached = cache.get(cache_key)
        if cached is not None:
            logger.info("Returning cached AI summary")
            return cached

        sections = []
        for section_key in ("activity", "hubs", "alerts", "ai_performance"):
            label = section_key.replace("_", " ").title()
            data = stats.get(section_key)
            if data:
                sections.append(f"{label}: {json.dumps(data)}")

        prompt = (
            "Current reporting period data:\n"
            + "\n".join(sections)
        )

        try:
            client = Anthropic(api_key=settings.CLAUDE_API_KEY)
            response = client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=250,
                temperature=0.3,
                system=[
                    {
                        "type": "text",
                        "text": SPARK_SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            logger.info("Claude AI summary generated (%d chars)", len(text))
            ttl = max(config.frequency_interval_minutes * 60, 60)
            cache.set(cache_key, text, timeout=ttl)
            return text
        except Exception:
            logger.warning("Claude summary generation failed", exc_info=True)
            return None

    @staticmethod
    def create_report(is_auto: bool = False):
        from .models import AIReportingConfig, SituationReport

        config = AIReportingConfig.get_solo()
        if is_auto and not config.auto_reporting_enabled:
            return None

        stats = ReportGenerationService.gather_stats(config)

        if config.use_ai_summary:
            summary = ReportGenerationService.generate_ai_summary(stats, config)
            if not summary:
                summary = ReportGenerationService.build_summary_text(stats)
        else:
            summary = ReportGenerationService.build_summary_text(stats)

        report = SituationReport.objects.create(
            summary=summary, generated_by="ai", is_auto=is_auto
        )
        pdf_path = ReportGenerationService.generate_pdf(report.id, summary, stats)
        from django.core.files import File
        with open(pdf_path, "rb") as f:
            report.pdf_file.save(f"report_{report.id}.pdf", File(f))
        return report
