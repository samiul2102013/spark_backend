from .models import AIReportingConfig, MessageReviewConfig


SPARK_SYSTEM_PROMPT = (
    "You are a disaster response reporting assistant for SPARK (Strategic Platform for "
    "Automated Response and Knowledge). Generate structured situation reports for government officials.\n\n"
    "RULES:\n"
    "- Use ONLY the numbers provided — never invent data\n"
    "- Be specific with counts, locations, and severity\n"
    "- Use professional, factual language\n"
    "- Output ONLY valid JSON — no markdown, no code fences, no prefixes\n\n"
    "OUTPUT FORMAT — return a JSON object with these keys:\n"
    '1. "abstract": {\n'
    '   "summary": "2-3 sentence narrative overview",\n'
    '   "status": "ESCALATING|STABLE|DECALATING|STEADY",\n'
    '   "total_incidents": <int>,\n'
    '   "critical_count": <int>,\n'
    '   "period_start": "<ISO datetime>",\n'
    '   "period_end": "<ISO datetime>"\n'
    "}\n"
    '2. "hazard_classification": {\n'
    '   "entries": [\n'
    '     {"hazard_type": "<name>", "default": "CRITICAL|HIGH|MEDIUM|LOW", '
    '"final": "CRITICAL|HIGH|MEDIUM|LOW", "basis": "<explanation>"}\n'
    "   ],\n"
    '   "escalation_rules": "<rule text>"\n'
    "}\n"
    '3. "triage": {\n'
    '   "entries": [\n'
    '     {"severity": "CRITICAL|HIGH|MEDIUM|LOW", "incident": "<name>", '
    '"locations": "<places>", "count": <int>, "status": "Active|Pending", "notes": "<text>"}\n'
    "   ],\n"
    '   "concurrent_incidents": <int>\n'
    "}\n"
    '4. "triage_rationale": {\n'
    '   "CRITICAL": "<paragraph>",\n'
    '   "HIGH": "<paragraph>",\n'
    '   "MEDIUM": "<paragraph>"\n'
    "}\n"
    '5. "statistics": {\n'
    '   "hazards": {"total_reported": <int>, "active": <int>, "pending_review": <int>, '
    '"auto_classified": <int>, "manually_reviewed": <int>, "resolved": <int>},\n'
    '   "hubs": {"total": <int>, "operational": <int>, "low_battery": <int>, '
    '"offline": <int>, "silent_communities": <int>},\n'
    '   "checkins": {"last_24h": <int>, "auto_scored": <int>, "pending_review": <int>, '
    '"need_assistance": <int>}\n'
    "}\n"
    '6. "recommendations": [\n'
    '   {"priority": "IMMEDIATE|URGENT|HIGH|MEDIUM", "action": "<verb>", '
    '"location": "<place>", "task": "<description>", "reason": "<explanation>"}\n'
    "]"
)


SPARK_STRUCTURED_SYSTEM_PROMPT = (
    "You are a disaster response triage and reporting assistant for SPARK. "
    "Analyze the provided incident data and previous report context. "
    "Output ONLY a valid JSON object with exactly six keys: "
    "abstract, hazard_classification, triage, triage_rationale, statistics, recommendations. "
    "Be concise, factual, and use only the data provided. "
    "Use escalation rules: Rule 1 = community silence (no check-ins in 3h), "
    "Rule 2 = hub offline or <20% battery, "
    "Rule 3 = 3+ same-type reports from same community, "
    "Rule 4 = active 6+ hours with no update."
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
            hazards_sev3 = Hazard.objects.filter(severity=3).values(
                "id", "category", "description", "latitude", "longitude",
                "hub__name", "created_at",
            )
            stats["classification"] = {
                "hazards_by_category": {
                    c: Hazard.objects.filter(category=c).count()
                    for c, _ in Hazard.CATEGORY_CHOICES
                },
                "hazards_by_severity": {
                    str(s): Hazard.objects.filter(severity=s).count()
                    for s in (1, 2, 3)
                },
                "high_severity_hazards": [
                    {**h, "created_at": h["created_at"].isoformat() if h["created_at"] else None}
                    for h in hazards_sev3[:20]
                ],
                "new_high_severity": [
                    {**h, "created_at": h["created_at"].isoformat() if h["created_at"] else None}
                    for h in new_hazards.filter(severity=3).values(
                        "id", "category", "description", "latitude", "longitude",
                        "hub__name", "created_at",
                    )[:10]
                ],
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
            required = {"abstract", "hazard_classification", "triage",
                         "triage_rationale", "statistics", "recommendations"}
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
        from apps.hazards.models import Hazard
        from apps.comms.models import CheckIn

        extraction = delta_data.get("extraction", {})
        classification = delta_data.get("classification", {})
        triage_data = delta_data.get("triage", {})
        hubs = delta_data.get("hubs", {})

        cats = classification.get("hazards_by_category", {})
        sorted_cats = sorted(cats.items(), key=lambda x: x[1], reverse=True)

        critical_list = triage_data.get("active_critical_hazards", [])
        assistance_list = triage_data.get("pending_assistance_checkins", [])

        total_hazards = extraction.get("total_hazards_all", 0)
        active_count = Hazard.objects.filter(status="active").count()
        pending_review = Hazard.objects.filter(review_status="pending").count()
        auto_classified = Hazard.objects.filter(risk_score__isnull=False).count()
        manual_reviewed = Hazard.objects.filter(review_status="reviewed").count()
        resolved = Hazard.objects.filter(review_status="resolved").count()

        total_hubs = hubs.get("total", 0)
        operational = hubs.get("open", 0)
        low_battery = hubs.get("low_battery", 0)
        offline = hubs.get("closed", 0) + hubs.get("critical", 0)
        silent = Hazard.objects.filter(hub__checkins__isnull=True).count()

        checkins_24h = extraction.get("new_checkins_need_assistance", 0)
        checkins_auto = 0
        checkins_pending = CheckIn.objects.filter(review_status="pending").count()
        checkins_need = CheckIn.objects.filter(status="need_assistance").count()

        hazard_entries = []
        for cat, count in sorted_cats:
            high_count = Hazard.objects.filter(category=cat, severity=3).count()
            if count == 0 and high_count == 0:
                continue
            default = "CRITICAL" if high_count > 0 else "HIGH" if count > 2 else "MEDIUM" if count > 0 else "LOW"
            final = default
            basis = f"{count} reports, {high_count} high severity"
            hazard_entries.append({
                "hazard_type": cat.replace("_", " ").title(),
                "default": default,
                "final": final,
                "basis": basis,
            })

        triage_entries = []
        for h in critical_list[:5]:
            category = h.get("category") or "Unknown"
            triage_entries.append({
                "severity": "CRITICAL",
                "incident": category.replace("_", " ").title(),
                "locations": h.get("hub__name") or f"({h.get('latitude')}, {h.get('longitude')})",
                "count": 1,
                "status": "Active",
                "notes": h.get("description", "")[:100],
            })
        for c in assistance_list[:5]:
            assistance = c.get("assistance_type") or "Assistance needed"
            triage_entries.append({
                "severity": "HIGH",
                "incident": assistance.replace("_", " ").title(),
                "locations": c.get("hub") or "Unknown",
                "count": c.get("people_count", 1),
                "status": "Active",
                "notes": f"{c.get('user', 'Unknown')} needs help",
            })

        return {
            "abstract": {
                "summary": (
                    f"{total_hazards} active incidents, {len(critical_list)} critical. "
                    f"{operational} of {total_hubs} hubs online. "
                    f"{assistance_list} pending assistance requests."
                ),
                "status": "ESCALATING" if len(critical_list) > 3 else "STABLE",
                "total_incidents": total_hazards,
                "critical_count": len(critical_list),
                "period_start": delta_data.get("period_start", ""),
                "period_end": delta_data.get("period_end", ""),
            },
            "hazard_classification": {
                "entries": hazard_entries or [
                    {"hazard_type": "None", "default": "LOW", "final": "LOW", "basis": "No hazards reported"}
                ],
                "escalation_rules": "Rule 1: community silence | Rule 2: hub offline or <20% battery | Rule 3: 3+ same-type reports from same community | Rule 4: active 6+ hours with no update",
            },
            "triage": {
                "entries": triage_entries or [
                    {"severity": "LOW", "incident": "None", "locations": "N/A", "count": 0, "status": "Pending", "notes": "No active incidents"}
                ],
                "concurrent_incidents": len(critical_list) + len(assistance_list),
            },
            "triage_rationale": {
                "CRITICAL": f"{len(critical_list)} critical incidents require immediate attention. "
                           f"Affected areas: {', '.join(set(h.get('hub__name', 'Unknown') for h in critical_list))}.",
                "HIGH": f"{len(assistance_list)} assistance requests pending.",
                "MEDIUM": "Monitor and assign when resources allow.",
            },
            "statistics": {
                "hazards": {
                    "total_reported": total_hazards,
                    "active": active_count,
                    "pending_review": pending_review,
                    "auto_classified": auto_classified,
                    "manually_reviewed": manual_reviewed,
                    "resolved": resolved,
                },
                "hubs": {
                    "total": total_hubs,
                    "operational": operational,
                    "low_battery": low_battery,
                    "offline": offline,
                    "silent_communities": silent,
                },
                "checkins": {
                    "last_24h": checkins_24h,
                    "auto_scored": checkins_auto,
                    "pending_review": checkins_pending,
                    "need_assistance": checkins_need,
                },
            },
            "recommendations": [
                {
                    "priority": "IMMEDIATE",
                    "action": "Deploy",
                    "location": "Affected areas",
                    "task": "Respond to critical incidents",
                    "reason": f"{len(critical_list)} active critical hazards require immediate response.",
                },
                {
                    "priority": "URGENT",
                    "action": "Contact",
                    "location": "Silent communities",
                    "task": "Establish communication with areas reporting no check-ins",
                    "reason": "Silent communities may indicate infrastructure failure or displacement.",
                },
            ],
        }

    @staticmethod
    def generate_pdf(report_id: int, report_data: dict) -> str:
        import os
        from datetime import datetime
        from django.conf import settings
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
        )
        from reportlab.lib.enums import TA_LEFT, TA_CENTER

        reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        filepath = os.path.join(reports_dir, f"report_{report_id}.pdf")

        doc = SimpleDocTemplate(
            filepath, pagesize=letter,
            leftMargin=0.6 * inch, rightMargin=0.6 * inch,
            topMargin=0.6 * inch, bottomMargin=0.6 * inch,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("ReportTitle", parent=styles["Title"],
            fontSize=20, leading=24, spaceAfter=4, textColor=colors.HexColor("#1a1a2e"))
        subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"],
            fontSize=9, leading=11, textColor=colors.HexColor("#666666"), spaceAfter=2)
        section_style = ParagraphStyle("Section", parent=styles["Heading2"],
            fontSize=13, leading=16, spaceBefore=12, spaceAfter=6,
            textColor=colors.HexColor("#1a1a2e"), borderWidth=0)
        body_style = ParagraphStyle("Body", parent=styles["Normal"],
            fontSize=9, leading=12, spaceAfter=4)
        cell_style = ParagraphStyle("Cell", parent=styles["Normal"],
            fontSize=7.5, leading=9, spaceAfter=0)
        header_cell = ParagraphStyle("HeaderCell", parent=styles["Normal"],
            fontSize=8, leading=10, textColor=colors.white, spaceAfter=0)
        rationale_style = ParagraphStyle("Rationale", parent=styles["Normal"],
            fontSize=9, leading=12, spaceAfter=6, spaceBefore=4)
        status_style = ParagraphStyle("Status", parent=styles["Normal"],
            fontSize=12, leading=14, textColor=colors.HexColor("#cc3333"), spaceAfter=6)

        now = datetime.now()
        elements = []

        elements.append(Paragraph("SPARK AI SITUATION REPORT", title_style))
        elements.append(Paragraph(
            f"Report #{report_id}  |  {now.strftime('%B %d, %Y')}  |  "
            f"{now.strftime('%I:%M %p')} Jamaica Time  |  Active Event Window",
            subtitle_style))

        abstract = report_data.get("abstract", {})
        status = abstract.get("status", "STABLE")
        status_color = colors.HexColor("#cc3333") if status == "ESCALATING" else \
                       colors.HexColor("#e68a00") if status == "ESCALATING" else \
                       colors.HexColor("#2d862d")
        elements.append(Paragraph(f"<b>{status}</b>", ParagraphStyle("StatusLine",
            parent=status_style, textColor=status_color, fontSize=14, spaceBefore=2, spaceAfter=8)))

        elements.append(Paragraph("<b>A  Abstract</b>", section_style))
        elements.append(Paragraph(abstract.get("summary", "No data available."), body_style))

        # B  Hazard Classification
        elements.append(Paragraph("<b>B  Hazard Classification</b>", section_style))
        hc = report_data.get("hazard_classification", {})
        hc_entries = hc.get("entries", [])
        if hc_entries:
            hc_data = [[Paragraph("Hazard Type", header_cell),
                        Paragraph("Default", header_cell),
                        Paragraph("Final", header_cell),
                        Paragraph("Classification Basis", header_cell)]]
            for e in hc_entries:
                hc_data.append([
                    Paragraph(e.get("hazard_type", ""), cell_style),
                    Paragraph(e.get("default", ""), cell_style),
                    Paragraph(e.get("final", ""), cell_style),
                    Paragraph(e.get("basis", ""), cell_style),
                ])
            hc_table = Table(hc_data, colWidths=[1.4*inch, 0.7*inch, 0.7*inch, 3.8*inch])
            hc_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(hc_table)
        elements.append(Paragraph(hc.get("escalation_rules", ""), ParagraphStyle(
            "Rules", parent=body_style, fontSize=7.5, textColor=colors.HexColor("#888888"), spaceBefore=4)))

        # C  Triage
        elements.append(Paragraph("<b>C  Triage</b>", section_style))
        triage = report_data.get("triage", {})
        triage_entries = triage.get("entries", [])
        if triage_entries:
            triage_data = [[Paragraph("Severity", header_cell),
                            Paragraph("Incident", header_cell),
                            Paragraph("Location(s)", header_cell),
                            Paragraph("Ct.", header_cell),
                            Paragraph("Status", header_cell),
                            Paragraph("Notes", header_cell)]]
            for e in triage_entries:
                sev = e.get("severity", "")
                sev_color = colors.HexColor("#cc3333") if sev == "CRITICAL" else \
                            colors.HexColor("#e68a00") if sev == "HIGH" else \
                            colors.HexColor("#2d862d") if sev == "MEDIUM" else \
                            colors.HexColor("#666666")
                triage_data.append([
                    Paragraph(f'<font color="{sev_color.hexval()}"><b>{sev}</b></font>', cell_style),
                    Paragraph(e.get("incident", ""), cell_style),
                    Paragraph(e.get("locations", ""), cell_style),
                    Paragraph(str(e.get("count", 0)), cell_style),
                    Paragraph(e.get("status", ""), cell_style),
                    Paragraph(e.get("notes", ""), cell_style),
                ])
            t_table = Table(triage_data, colWidths=[0.7*inch, 1.3*inch, 1.2*inch, 0.4*inch, 0.6*inch, 2.4*inch])
            t_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (3, 0), (3, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(t_table)

        # D  Triage Rationale
        elements.append(Paragraph("<b>D  Triage Rationale</b>", section_style))
        rationale = report_data.get("triage_rationale", {})
        for level in ("CRITICAL", "HIGH", "MEDIUM"):
            text = rationale.get(level, "")
            if text:
                level_color = colors.HexColor("#cc3333") if level == "CRITICAL" else \
                              colors.HexColor("#e68a00") if level == "HIGH" else \
                              colors.HexColor("#2d862d")
                elements.append(Paragraph(
                    f'<font color="{level_color.hexval()}"><b>{level}</b></font>', body_style))
                elements.append(Paragraph(text, rationale_style))

        # E  Statistics Breakdown
        elements.append(Paragraph("<b>E  Statistics Breakdown</b>", section_style))
        stats = report_data.get("statistics", {})

        def make_stats_table(title, data_dict, key_order):
            table_data = [[Paragraph(title, header_cell)]]
            for key in key_order:
                val = data_dict.get(key, 0)
                label = key.replace("_", " ").title()
                table_data.append([
                    Paragraph(f"<b>{label}</b>", cell_style),
                    Paragraph(str(val), cell_style),
                ])
            t = Table(table_data, colWidths=[1.8*inch, 0.8*inch])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]))
            return t

        haz_stats = stats.get("hazards", {})
        hub_stats = stats.get("hubs", {})
        ci_stats = stats.get("checkins", {})

        stat_tables = []
        if haz_stats:
            stat_tables.append(make_stats_table(
                "Hazard Status", haz_stats,
                ["total_reported", "active", "pending_review", "auto_classified", "manually_reviewed", "resolved"]))
        if hub_stats:
            stat_tables.append(make_stats_table(
                "Hub Status", hub_stats,
                ["total", "operational", "low_battery", "offline", "silent_communities"]))
        if ci_stats:
            stat_tables.append(make_stats_table(
                "Check-in Status", ci_stats,
                ["last_24h", "auto_scored", "pending_review", "need_assistance"]))

        if stat_tables:
            stat_grid = Table([[stat_tables[i] if i < len(stat_tables) else ""
                                for i in range(3)]],
                              colWidths=[2.8*inch, 2.8*inch, 2.8*inch])
            stat_grid.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(stat_grid)

        # F  Coordinator Recommendations
        elements.append(Paragraph("<b>F  Coordinator Recommendations</b>", section_style))
        recs = report_data.get("recommendations", [])
        if recs:
            rec_data = [[Paragraph("#", header_cell),
                         Paragraph("Priority", header_cell),
                         Paragraph("Action / Location", header_cell),
                         Paragraph("Task", header_cell),
                         Paragraph("Reason", header_cell)]]
            for i, r in enumerate(recs, 1):
                pri = r.get("priority", "")
                pri_color = colors.HexColor("#cc3333") if pri == "IMMEDIATE" else \
                            colors.HexColor("#e68a00") if pri == "URGENT" else \
                            colors.HexColor("#2d862d") if pri == "HIGH" else \
                            colors.HexColor("#666666")
                action = r.get("action", "")
                location = r.get("location", "")
                action_loc = f"{action} — {location}" if action and location else action or location
                rec_data.append([
                    Paragraph(str(i), cell_style),
                    Paragraph(f'<font color="{pri_color.hexval()}"><b>{pri}</b></font>', cell_style),
                    Paragraph(action_loc, cell_style),
                    Paragraph(r.get("task", ""), cell_style),
                    Paragraph(r.get("reason", ""), cell_style),
                ])
            r_table = Table(rec_data, colWidths=[0.3*inch, 0.7*inch, 1.2*inch, 2.0*inch, 2.4*inch])
            r_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(r_table)

        model = settings.CLAUDE_MODEL
        footer = Paragraph(
            f"This report was generated by SPARK using Claude ({model}). "
            "Hazard classification and escalation are based on incoming report data only. "
            "Field verification is required before deploying emergency resources.",
            ParagraphStyle("Footer", parent=body_style, fontSize=7.5, textColor=colors.HexColor("#888888"),
                           spaceBefore=12, spaceAfter=0))
        elements.append(footer)

        doc.build(elements)
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
        if last_report:
            previous_context = {
                "abstract": last_report.extraction,
                "hazard_classification": last_report.hazard_classification,
                "triage": last_report.triage,
                "triage_rationale": None,
                "statistics": None,
                "recommendations": None,
            }

        delta_data = ReportGenerationService.gather_delta_stats(config, since=since)

        if config.structured_reporting:
            ai_result = ReportGenerationService.generate_structured_report(
                delta_data, previous_context, config
            )
            if ai_result:
                report_data = {
                    "abstract": ai_result.get("abstract") or {},
                    "hazard_classification": ai_result.get("hazard_classification") or {},
                    "triage": ai_result.get("triage") or {},
                    "triage_rationale": ai_result.get("triage_rationale") or {},
                    "statistics": ai_result.get("statistics") or {},
                    "recommendations": ai_result.get("recommendations") or [],
                }
            else:
                report_data = ReportGenerationService.build_fallback_structured(delta_data)

            summary = report_data["abstract"].get("summary", "No summary available.")
            extraction = report_data["abstract"]
            hazard_classification = report_data["hazard_classification"]
            triage = report_data["triage"]
        else:
            if config.use_ai_summary:
                summary = ReportGenerationService.generate_ai_summary(delta_data, config)
                if not summary:
                    summary = ReportGenerationService.build_summary_text(delta_data)
            else:
                summary = ReportGenerationService.build_summary_text(delta_data)
            report_data = None
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
            context_snapshot=report_data or delta_data,
            report_period_start=period_start,
            report_period_end=period_end,
            generated_by="ai",
            is_auto=is_auto,
        )

        pdf_path = ReportGenerationService.generate_pdf(
            report.id, report_data or {"abstract": {"summary": summary}}
        )
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