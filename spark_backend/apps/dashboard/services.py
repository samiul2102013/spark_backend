from datetime import datetime, timedelta

from django.db.models import Count, Q
from django.utils import timezone

from apps.ai.models import SituationReport
from apps.bookings.models import Booking
from apps.hazards.models import Hazard
from apps.hubs.models import Hub


class DashboardService:
    @staticmethod
    def overview():
        hubs_total = Hub.objects.count()
        hubs_open = Hub.objects.filter(status="open").count()
        hubs_critical = Hub.objects.filter(status="critical").count()
        hazards_active = Hazard.objects.filter(status="active").count()
        hazards_today = Hazard.objects.filter(
            created_at__date=timezone.now().date()
        ).count()
        bookings_active = Booking.objects.filter(status="active").count()
        bookings_today = Booking.objects.filter(
            start_time__date=timezone.now().date()
        ).count()

        return {
            "hubs": {
                "total": hubs_total,
                "open": hubs_open,
                "critical": hubs_critical,
            },
            "hazards": {
                "active": hazards_active,
                "reported_today": hazards_today,
            },
            "bookings": {
                "active": bookings_active,
                "today": bookings_today,
            },
        }

    @staticmethod
    def map_data():
        hubs = Hub.objects.values(
            "id", "name", "latitude", "longitude", "status", "battery_percentage"
        )
        hazards = Hazard.objects.filter(status="active").values(
            "id", "category", "latitude", "longitude", "severity"
        )
        return {
            "hubs": list(hubs),
            "hazards": list(hazards),
        }

    @staticmethod
    def situation_reports(hub_id=None):
        qs = SituationReport.objects.all()
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        return qs.order_by("-created_at")[:20]
