from datetime import timedelta

from django.db.models import Prefetch
from django.utils import timezone

from apps.comms.models import CheckIn, InboundMessage
from apps.hazards.models import Comment, Hazard
from apps.hubs.models import Hub


class GovService:

    def overview(self):
        today = timezone.now().date()
        now = timezone.now()
        twenty_four_hours_ago = now - timedelta(hours=24)

        checkins_total = CheckIn.objects.count()
        checkins_today_qs = CheckIn.objects.filter(timestamp__date=today)

        checkins_24h = CheckIn.objects.filter(timestamp__gte=twenty_four_hours_ago)
        checkins_over_time = []
        for i in range(8):
            bucket_start = twenty_four_hours_ago + timedelta(hours=i * 3)
            bucket_end = bucket_start + timedelta(hours=3)
            count = checkins_24h.filter(
                timestamp__gte=bucket_start, timestamp__lt=bucket_end
            ).count()
            label = f"{bucket_start.strftime('%H:%M')}-{bucket_end.strftime('%H:%M')}"
            checkins_over_time.append({"bucket": label, "count": count})

        return {
            "checkins": {
                "total": checkins_total,
                "today": checkins_today_qs.count(),
                "safe": checkins_today_qs.filter(status="safe").count(),
                "need_assistance": checkins_today_qs.filter(status="need_assistance").count(),
            },
            "active_hubs": Hub.objects.filter(status="open").count(),
            "hazard_reports": Hazard.objects.count(),
            "silent_communications": InboundMessage.objects.filter(status="pending").count(),
            "urgent_flags": {
                "medical_roadblocks": Hazard.objects.filter(
                    category="medical", status="active"
                ).count(),
                "flooding": Hazard.objects.filter(
                    category="flooding", status="active"
                ).count(),
            },
            "checkins_over_time": checkins_over_time,
            "hazard_breakdown": {
                "flooding": Hazard.objects.filter(category="flooding").count(),
                "fire": Hazard.objects.filter(category="fire").count(),
                "medical": Hazard.objects.filter(category="medical").count(),
            },
        }

    def map_data(self, bounds=None, category=None, data_type=None):
        result = {}

        if data_type is None or data_type == "hubs":
            hubs_qs = Hub.objects.all()
            if bounds:
                if all([bounds.get(k) for k in ("lat_min", "lat_max", "lng_min", "lng_max")]):
                    hubs_qs = hubs_qs.filter(
                        latitude__gte=bounds["lat_min"], latitude__lte=bounds["lat_max"],
                        longitude__gte=bounds["lng_min"], longitude__lte=bounds["lng_max"],
                    )
            medical_hubs = hubs_qs.values("id", "name", "latitude", "longitude")
            result["medical_hubs"] = {
                "count": medical_hubs.count(),
                "locations": list(medical_hubs),
            }

        if data_type is None or data_type in ("hazards", "fallen"):
            hazards_qs = Hazard.objects.select_related("reporter").all()
            if bounds:
                if all([bounds.get(k) for k in ("lat_min", "lat_max", "lng_min", "lng_max")]):
                    hazards_qs = hazards_qs.filter(
                        latitude__gte=bounds["lat_min"], latitude__lte=bounds["lat_max"],
                        longitude__gte=bounds["lng_min"], longitude__lte=bounds["lng_max"],
                    )
            if category and data_type != "fallen":
                hazards_qs = hazards_qs.filter(category=category)

            if data_type is None or data_type == "hazards":
                qs = hazards_qs if data_type == "hazards" else hazards_qs.exclude(category="fallen_tree")
                hazard_values = qs.values(
                    "id", "category", "severity", "status",
                    "latitude", "longitude", "description", "created_at",
                )
                result["hazards"] = list(hazard_values)

            if data_type is None or data_type == "fallen":
                fallen = hazards_qs.filter(category="fallen_tree").values(
                    "id", "category", "latitude", "longitude",
                    "description", "severity", "status", "created_at",
                )
                result["fall_incidents"] = list(fallen)

        if data_type is None or data_type == "medical_needs":
            medical_needs_qs = CheckIn.objects.filter(
                status="need_assistance",
            ).exclude(medical_notes="").select_related("user", "hub").values(
                "id", "user__full_name", "latitude", "longitude",
                "medical_notes", "people_count", "hub_id", "timestamp",
            )
            result["medical_needs"] = [
                {
                    "checkin_id": n["id"],
                    "user_name": n["user__full_name"],
                    "latitude": n["latitude"],
                    "longitude": n["longitude"],
                    "medical_notes": n["medical_notes"],
                    "people_count": n["people_count"],
                    "hub_id": n["hub_id"],
                    "timestamp": n["timestamp"],
                }
                for n in medical_needs_qs
            ]

        return result

    def hazard_detail(self, hazard_id):
        return Hazard.objects.select_related("reporter", "hub").prefetch_related(
            Prefetch(
                "comments",
                queryset=Comment.objects.select_related("author").order_by("created_at"),
            )
        ).get(id=hazard_id)

    def situation_reports(self):
        return [
            {
                "id": 1,
                "title": "Situation Report - Hub Alpha",
                "subtitle": "Daily assessment for June 25, 2026",
                "timestamp": "2026-06-25T06:00:00+00:00",
                "pdf_url": "https://api.chargesafe.com/media/reports/situation_report_1.pdf",
            },
            {
                "id": 2,
                "title": "Situation Report - Hub Beta",
                "subtitle": "Evening assessment for June 24, 2026",
                "timestamp": "2026-06-24T18:00:00+00:00",
                "pdf_url": "https://api.chargesafe.com/media/reports/situation_report_2.pdf",
            },
            {
                "id": 3,
                "title": "Situation Report - Hub Gamma",
                "subtitle": "Morning assessment for June 24, 2026",
                "timestamp": "2026-06-24T06:00:00+00:00",
                "pdf_url": "https://api.chargesafe.com/media/reports/situation_report_3.pdf",
            },
        ]

    def get_infrastructure(self, status=None):
        qs = Hub.objects.all()
        if status == "online":
            qs = qs.filter(status="open")
        elif status == "offline":
            qs = qs.exclude(status="open")
        return qs

    def get_infrastructure_hub(self, hub_id):
        return Hub.objects.get(id=hub_id)

    def list_hazards(self, severity=None, category=None, status=None):
        qs = Hazard.objects.select_related("reporter", "hub").all()
        if severity:
            qs = qs.filter(severity=severity)
        if category:
            qs = qs.filter(category=category)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")
