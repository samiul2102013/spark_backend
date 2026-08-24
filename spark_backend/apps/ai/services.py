from .models import AIReportingConfig, MessageReviewConfig


SPARK_SYSTEM_PROMPT = (
    "You are a disaster response reporting assistant for SPARK (Strategic Platform for "
    "Automated Response and Knowledge). Generate structured situation reports for government officials.\n\n"
    "RULES:\n"
    "- Use ONLY the numbers provided — never invent data\n"
    "- Be specific with counts, locations, and severity\n"
    "- Use professional, factual language\n"
    "- Do NOT add commentary, opinions, or speculative recommendations\n"
    "- Output ONLY valid JSON — no markdown, no code fences, no prefixes\n\n"
    "OUTPUT FORMAT — return a JSON object with these three keys:\n"
    '1. "extraction": {\n'
    '   "summary": "1-2 sentence overview of the reporting period",\n'
    '   "total_hazards": <int>,\n'
    '   "total_checkins_need_assistance": <int>,\n'
    '   "total_hubs_online": <int>,\n'
    '   "period_start": "<ISO datetime>",\n'
    '   "period_end": "<ISO datetime>"\n'
    "}\n"
    '2. "hazard_classification": {\n'
    '   "categories": [{"category": "<name>", "count": <int>, "high_severity": <int>}],\n'
    '   "most_common_category": "<name>",\n'
    '   "total_high_severity": <int>,\n'
    '   "new_hazards_since_last": <int>\n'
    "}\n"
    '3. "triage": {\n'
    '   "priorities": [\n'
    '     {"priority": "critical|high|medium|low", "incident": "<description>", '
    '"location": "<area>", "details": "<specifics>"}\n'
    "   ],\n"
    '   "resource_needs": ["<need>"],\n'
    '   "affected_areas": ["<area>"],\n'
    '   "concurrent_incidents": <int>,\n'
    '   "overall_assessment": "<1-2 sentence triage assessment>"\n'
    "}"
)


SPARK_STRUCTURED_SYSTEM_PROMPT = (
    "You are a disaster response triage and reporting assistant for SPARK. "
    "Analyze the provided incident data and previous report context. "
    "Output ONLY a valid JSON object with exactly three keys: extraction, hazard_classification, triage. "
    "Be concise, factual, and use only the data provided."
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
    def _get_last_report() -> tuple:
        from .models import SituationReport

        return SituationReport.objects.filter(
            report_period_end__isnull=False
        ).order_by("-report_period_end").first()

    @staticmethod
    def gather_delta_stats(config, since=None) -> dict:
        from datetime import timedelta
        from django.utils import timezone
        from apps.hazards.models import Hazard
        from apps.comms.models import CheckIn
        from apps.hubs.models import Hub

        now = timezone.now()
        period_start = since or (now - timedelta(hours=24))
        period_end = now

        stats = {
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
        }

        new_hazards = Hazard.objects.filter(created_at__gte=period_start)

        new_checkins = CheckIn.objects.filter(timestamp__gte=period_start)

        if config.include_extraction:
            stats["extraction"] = {
                "new_hazards": new_hazards.count(),
                "new_hazards_by_category": {
                    c: new_hazards.filter(category=c).count()
                    for c, _ in Hazard.CATEGORY_CHOICES
                },
                "new_checkins_need_assistance": new_checkins.filter(
                    status="need_assistance"
                ).count(),
                "total_hubs_online": Hub.objects.filter(status="open").count(),
                "total_hubs_low_battery": Hub.objects.filter(battery_percentage__lt=20).count(),
                "total_hazards_all": Hazard.objects.count(),
                "total_checkins_all": CheckIn.objects.count(),
            }

        if config.include_classification:
            stats["classification"] = {
                "hazards_by_category": {
                    c: Hazard.objects.filter(category=c).count()
                    for c, _ in Hazard.CATEGORY_CHOICES
                },
                "hazards_by_severity": {
                    str(s): Hazard.objects.filter(severity=s).count()
                    for s in (1, 2, 3)
                },
                "high_severity_hazards": list(
                    Hazard.objects.filter(severity=3).values(
                        "id", "category", "description", "latitude", "longitude",
                        "hub__name", "created_at",
                    )[:20]
                ),
                "new_high_severity": list(
                    new_hazards.filter(severity=3).values(
                        "id", "category", "description", "latitude", "longitude",
                        "hub__name", "created_at",
                    )[:10]
                ),
            }

        if config.include_triage:
            critical = Hazard.objects.filter(
                severity=3, status="active", review_status__in=("pending", "escalated")
            )[:15]
            need_help = CheckIn.objects.filter(
                status="need_assistance", review_status__in=("pending", "escalated")
            )[:15]
            stats["triage"] = {
                "active_critical_hazards": [
                    {
                        "id": h.id,
                        "category": h.category,
                        "severity": h.severity,
                        "description": h.description[:200],
                        "latitude": float(h.latitude),
                        "longitude": float(h.longitude),
                        "hub": h.hub.name if h.hub else None,
                        "created_at": h.created_at.isoformat(),
                    }
                    for h in critical
                ],
                "pending_assistance_checkins": [
                    {
                        "id": c.id,
                        "user": c.user.full_name if c.user else None,
                        "hub": c.hub.name if c.hub else None,
                        "assistance_type": c.assistance_type,
                        "people_count": c.people_count,
                        "latitude": float(c.latitude) if c.latitude else None,
                        "longitude": float(c.longitude) if c.longitude else None,
                        "created_at": c.timestamp.isoformat(),
                    }
                    for c in need_help
                ],
                "total_active_critical": Hazard.objects.filter(
                    severity=3, status="active"
                ).count(),
                "total_pending_assistance": CheckIn.objects.filter(
                    status="need_assistance", review_status="pending"
                ).count(),
            }

        if config.include_hubs_summary:
            stats["hubs"] = {
                "total": Hub.objects.count(),
                "open": Hub.objects.filter(status="open").count(),
                "closed": Hub.objects.filter(status="closed").count(),
                "critical": Hub.objects.filter(status="critical").count(),
                "low_battery": Hub.objects.filter(battery_percentage__lt=20).count(),
            }

        return stats

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
        for section_key in ("extraction", "classification", "triage", "hubs"):
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
    def generate_structured_report(delta_data: dict, previous_context: dict | None, config) -> dict | None:
        import json
        import logging

        from django.conf import settings
        from anthropic import Anthropic

        logger = logging.getLogger(__name__)

        if not settings.CLAUDE_API_KEY:
            logger.warning("CLAUDE_API_KEY not set — cannot generate structured report")
            return None

        prompt_parts = []

        if previous_context:
            prompt_parts.append(
                "PREVIOUS REPORT CONTEXT:\n"
                + json.dumps(previous_context, indent=2)
            )

        prompt_parts.append(
            "CURRENT PERIOD DATA:\n"
            + json.dumps(delta_data, indent=2)
        )

        prompt_parts.append(
            "\nBased on the data above and the previous report context, "
            "generate the current situation report as a JSON object with exactly "
            "three keys: extraction, hazard_classification, triage. "
            "Be concise and factual."
        )

        prompt = "\n\n".join(prompt_parts)

        try:
            client = Anthropic(api_key=settings.CLAUDE_API_KEY)
            response = client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=800,
                temperature=0.1,
                system=[
                    {
                        "type": "text",
                        "text": SPARK_STRUCTURED_SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": prompt}],
            )

            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]
                if raw.endswith("```"):
                    raw = raw[:-3]
            raw = raw.strip()

            result = json.loads(raw)
            required = {"extraction", "hazard_classification", "triage"}
            if not required.issubset(result.keys()):
                logger.warning(
                    "Claude returned incomplete structure — missing %s",
                    required - result.keys(),
                )
                return None

            logger.info("Claude structured report generated successfully")
            return result

        except json.JSONDecodeError:
            logger.warning("Claude returned invalid JSON", exc_info=True)
            return None
        except Exception:
            logger.warning("Claude structured report generation failed", exc_info=True)
            return None

    @staticmethod
    def build_fallback_structured(delta_data: dict) -> dict:
        extraction = delta_data.get("extraction", {})
        classification = delta_data.get("classification", {})
        triage_data = delta_data.get("triage", {})

        cats = classification.get("hazards_by_category", {})
        sorted_cats = sorted(cats.items(), key=lambda x: x[1], reverse=True)

        critical_list = triage_data.get("active_critical_hazards", [])
        assistance_list = triage_data.get("pending_assistance_checkins", [])

        return {
            "extraction": {
                "summary": (
                    f"{extraction.get('new_hazards', 0)} new hazards reported, "
                    f"{extraction.get('new_checkins_need_assistance', 0)} new assistance requests. "
                    f"{extraction.get('total_hubs_online', 0)} of {delta_data.get('hubs', {}).get('total', 0)} hubs online."
                ),
                "total_hazards": extraction.get("total_hazards_all", 0),
                "total_checkins_need_assistance": extraction.get("total_checkins_all", 0),
                "total_hubs_online": extraction.get("total_hubs_online", 0),
                "period_start": delta_data.get("period_start", ""),
                "period_end": delta_data.get("period_end", ""),
            },
            "hazard_classification": {
                "categories": [
                    {"category": cat, "count": count, "high_severity": 0}
                    for cat, count in sorted_cats[:8]
                ],
                "most_common_category": sorted_cats[0][0] if sorted_cats else "none",
                "total_high_severity": classification.get("hazards_by_severity", {}).get("3", 0),
                "new_hazards_since_last": extraction.get("new_hazards", 0),
            },
            "triage": {
                "priorities": [
                    {
                        "priority": "critical",
                        "incident": h.get("description", "Unknown critical hazard")[:100],
                        "location": h.get("hub__name") or f"({h.get('latitude')}, {h.get('longitude')})",
                        "details": f"{h.get('category')} — severity 3",
                    }
                    for h in critical_list[:5]
                ] + [
                    {
                        "priority": "high",
                        "incident": c.get("assistance_type") or "Assistance needed",
                        "location": c.get("hub") or f"({c.get('latitude')}, {c.get('longitude')})",
                        "details": f"{c.get('people_count')} person(s) — {c.get('user')}",
                    }
                    for c in assistance_list[:5]
                ],
                "resource_needs": [
                    "Medical evacuation" if any(
                        c.get("assistance_type") == "medical" for c in assistance_list
                    ) else None,
                    "Road clearance" if any(
                        h.get("category") in ("blocked_road", "fallen_tree")
                        for h in critical_list
                    ) else None,
                ],
                "affected_areas": list(set(
                    [h.get("hub__name") for h in critical_list if h.get("hub__name")]
                    + [c.get("hub") for c in assistance_list if c.get("hub")]
                )),
                "concurrent_incidents": len(critical_list) + len(assistance_list),
                "overall_assessment": (
                    f"{len(critical_list)} critical hazards and "
                    f"{len(assistance_list)} pending assistance requests require immediate attention."
                ),
            },
        }

    @staticmethod
    def generate_pdf(report_id: int, report_data: dict) -> str:
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

        c.setFont("Helvetica-Bold", 20)
        c.drawString(inch, height - 0.8 * inch, "SPARK Situation Report")

        c.setFont("Helvetica", 9)
        c.drawString(inch, height - 1.2 * inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")

        extraction = report_data.get("extraction", {})
        classification = report_data.get("hazard_classification", {})
        triage = report_data.get("triage", {})

        y = height - 1.8 * inch

        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, y, "1. Extraction")
        y -= 0.35 * inch
        c.setFont("Helvetica", 10)
        summary = extraction.get("summary", "No data available.")
        from reportlab.lib.utils import simpleSplit
        max_width = width - 2 * inch
        for line in simpleSplit(summary, "Helvetica", 10, max_width):
            c.drawString(inch + 10, y, line)
            y -= 0.3 * inch
            if y < 0.8 * inch:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - inch

        y -= 0.15 * inch
        for key in ("total_hazards", "total_checkins_need_assistance", "total_hubs_online"):
            val = extraction.get(key)
            if val is not None:
                c.drawString(inch + 10, y, f"{key.replace('_', ' ').title()}: {val}")
                y -= 0.25 * inch
                if y < 0.8 * inch:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = height - inch

        y -= 0.2 * inch
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, y, "2. Hazard Classification")
        y -= 0.35 * inch
        c.setFont("Helvetica", 10)

        for cat in classification.get("categories", []):
            line = f"{cat.get('category', 'Unknown')}: {cat.get('count', 0)} ({cat.get('high_severity', 0)} high severity)"
            c.drawString(inch + 10, y, line)
            y -= 0.25 * inch
            if y < 0.8 * inch:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - inch

        c.drawString(inch + 10, y, f"Most common: {classification.get('most_common_category', 'N/A')}")
        y -= 0.25 * inch
        c.drawString(inch + 10, y, f"Total high severity: {classification.get('total_high_severity', 0)}")
        y -= 0.25 * inch
        c.drawString(inch + 10, y, f"New since last report: {classification.get('new_hazards_since_last', 0)}")

        y -= 0.3 * inch
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, y, "3. Triage")
        y -= 0.35 * inch
        c.setFont("Helvetica", 10)

        for item in triage.get("priorities", []):
            pri = item.get("priority", "unknown").upper()
            inc = item.get("incident", "Unknown")
            loc = item.get("location", "Unknown")
            line = f"[{pri}] {inc} — {loc}"
            for wrapped in simpleSplit(line, "Helvetica", 10, max_width):
                c.drawString(inch + 10, y, wrapped)
                y -= 0.25 * inch
                if y < 0.8 * inch:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = height - inch

        y -= 0.15 * inch
        c.setFont("Helvetica-Bold", 10)
        c.drawString(inch + 10, y, "Resource Needs:")
        y -= 0.25 * inch
        c.setFont("Helvetica", 10)
        for need in triage.get("resource_needs", []):
            if need:
                c.drawString(inch + 20, y, f"- {need}")
                y -= 0.25 * inch
                if y < 0.8 * inch:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = height - inch

        c.setFont("Helvetica-Bold", 10)
        c.drawString(inch + 10, y, "Affected Areas:")
        y -= 0.25 * inch
        c.setFont("Helvetica", 10)
        for area in triage.get("affected_areas", []):
            c.drawString(inch + 20, y, f"- {area}")
            y -= 0.25 * inch
            if y < 0.8 * inch:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - inch

        y -= 0.15 * inch
        c.drawString(inch + 10, y, f"Concurrent incidents: {triage.get('concurrent_incidents', 0)}")

        y -= 0.3 * inch
        c.setFont("Helvetica-Oblique", 10)
        assessment = triage.get("overall_assessment", "")
        for line in simpleSplit(assessment, "Helvetica-Oblique", 10, max_width):
            c.drawString(inch + 10, y, line)
            y -= 0.25 * inch
            if y < 0.8 * inch:
                c.showPage()
                c.setFont("Helvetica-Oblique", 10)
                y = height - inch

        c.save()
        return filepath

    @staticmethod
    def create_report(is_auto: bool = False):
        import json
        from django.utils import timezone

        from .models import AIReportingConfig, SituationReport

        config = AIReportingConfig.get_solo()
        if is_auto and not config.auto_reporting_enabled:
            return None

        last_report = ReportGenerationService._get_last_report()
        since = last_report.report_period_end if last_report else None
        previous_context = None
        if last_report and last_report.extraction:
            previous_context = {
                "extraction": last_report.extraction,
                "hazard_classification": last_report.hazard_classification,
                "triage": last_report.triage,
            }

        delta_data = ReportGenerationService.gather_delta_stats(config, since=since)

        if config.structured_reporting:
            ai_result = ReportGenerationService.generate_structured_report(
                delta_data, previous_context, config
            )
            if ai_result:
                extraction = ai_result.get("extraction") or {}
                hazard_classification = ai_result.get("hazard_classification") or {}
                triage = ai_result.get("triage") or {}
            else:
                fallback = ReportGenerationService.build_fallback_structured(delta_data)
                extraction = fallback["extraction"]
                hazard_classification = fallback["hazard_classification"]
                triage = fallback["triage"]

            summary = extraction.get("summary", "No summary available.")
        else:
            if config.use_ai_summary:
                summary = ReportGenerationService.generate_ai_summary(delta_data, config)
                if not summary:
                    summary = ReportGenerationService.build_summary_text(delta_data)
            else:
                summary = ReportGenerationService.build_summary_text(delta_data)
            extraction = None
            hazard_classification = None
            triage = None

        period_end = timezone.now()
        period_start = since or (period_end - timezone.timedelta(hours=24))

        report = SituationReport.objects.create(
            summary=summary,
            extraction=extraction,
            hazard_classification=hazard_classification,
            triage=triage,
            context_snapshot=delta_data,
            report_period_start=period_start,
            report_period_end=period_end,
            generated_by="ai",
            is_auto=is_auto,
        )

        report_data = {
            "extraction": extraction or {},
            "hazard_classification": hazard_classification or {},
            "triage": triage or {},
        }
        pdf_path = ReportGenerationService.generate_pdf(report.id, report_data)
        from django.core.files import File
        with open(pdf_path, "rb") as f:
            report.pdf_file.save(f"report_{report.id}.pdf", File(f))
        return report

    @staticmethod
    def build_summary_text(stats: dict) -> str:
        parts = []

        extraction = stats.get("extraction")
        if extraction:
            parts.append(
                f"Activity: {extraction.get('new_hazards', 0)} new hazards, "
                f"{extraction.get('new_checkins_need_assistance', 0)} new assistance requests. "
                f"{extraction.get('total_hubs_online', 0)} hubs online."
            )

        classification = stats.get("classification")
        if classification:
            sev = classification.get("hazards_by_severity", {})
            parts.append(
                f"Hazards: {sev.get('3', 0)} high severity, "
                f"{sev.get('2', 0)} medium, {sev.get('1', 0)} low."
            )

        triage_data = stats.get("triage")
        if triage_data:
            parts.append(
                f"Alerts: {triage_data.get('total_active_critical', 0)} critical hazards active, "
                f"{triage_data.get('total_pending_assistance', 0)} assistance requests pending."
            )

        hubs = stats.get("hubs")
        if hubs:
            parts.append(
                f"Hubs: {hubs.get('open', 0)} active out of {hubs.get('total', 0)}, "
                f"{hubs.get('low_battery', 0)} low battery."
            )

        return " ".join(parts) if parts else "No data available for this reporting period."