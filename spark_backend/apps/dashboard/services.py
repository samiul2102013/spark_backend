from django.db.models import Count, Q
from django.utils import timezone

from apps.ai.models import SituationReport
from apps.bookings.models import Booking
from apps.comms.models import CheckIn
from apps.hazards.models import Hazard
from apps.hubs.models import Hub


class DashboardService:
    def overview(self):
        today = timezone.now().date()
        hubs_total = Hub.objects.count()
        hubs_open = Hub.objects.filter(status="open").count()
        hubs_critical = Hub.objects.filter(status="critical").count()
        hazards_active = Hazard.objects.filter(status="active").count()
        hazards_today = Hazard.objects.filter(created_at__date=today).count()
        bookings_active = Booking.objects.filter(status="active").count()
        bookings_today = Booking.objects.filter(start_time__date=today).count()
        checkins_today = CheckIn.objects.filter(timestamp__date=today)
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
            "checkins": {
                "total_today": checkins_today.count(),
                "safe": checkins_today.filter(status="safe").count(),
                "need_assistance": checkins_today.filter(status="need_assistance").count(),
            },
        }

    def map_data(self, bounds=None):
        hubs = Hub.objects.all()
        hazards = Hazard.objects.filter(status="active")
        if bounds:
            lat_min = bounds.get("lat_min")
            lat_max = bounds.get("lat_max")
            lng_min = bounds.get("lng_min")
            lng_max = bounds.get("lng_max")
            if all([lat_min, lat_max, lng_min, lng_max]):
                hubs = hubs.filter(
                    latitude__gte=lat_min, latitude__lte=lat_max,
                    longitude__gte=lng_min, longitude__lte=lng_max,
                )
                hazards = hazards.filter(
                    latitude__gte=lat_min, latitude__lte=lat_max,
                    longitude__gte=lng_min, longitude__lte=lng_max,
                )
        return {"hubs": hubs, "hazards": hazards}

    def situation_reports(self, hub_id=None):
        qs = SituationReport.objects.select_related("hub").all()
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        return qs.order_by("-created_at")

    def get_alerts(self, severity=None, status=None, hub_id=None):
        qs = Hazard.objects.select_related("reporter", "hub").all()
        if severity:
            qs = qs.filter(severity=severity)
        if status:
            qs = qs.filter(status=status)
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        return qs.order_by("-created_at")

    def get_infrastructure(self):
        today = timezone.now().date()
        return Hub.objects.annotate(
            checkins_today=Count("checkins", filter=Q(checkins__timestamp__date=today)),
            active_bookings=Count("bookings", filter=Q(bookings__status="active")),
        )

    def get_infrastructure_hub(self, hub_id):
        today = timezone.now().date()
        return Hub.objects.annotate(
            checkins_today=Count("checkins", filter=Q(checkins__timestamp__date=today)),
            active_bookings=Count("bookings", filter=Q(bookings__status="active")),
        ).get(id=hub_id)
