from datetime import timedelta

from django.utils import timezone

from apps.comms.models import CheckIn
from apps.hazards.models import Hazard


ALL_CATEGORIES = [
    "flooding",
    "fallen_tree",
    "blocked_road",
    "fallen_utility_pole",
    "medical",
    "fire",
    "collapsed_building",
    "power_line_down",
    "landslide",
    "earthquake",
    "storm",
    "other",
]


class DashboardService:
    def overview(self):
        today = timezone.now().date()

        hazard_breakdown = {}
        for cat in ALL_CATEGORIES:
            hazard_breakdown[cat] = Hazard.objects.filter(category=cat).count()

        checkins_today = CheckIn.objects.filter(timestamp__date=today)

        checkins = {
            "total": CheckIn.objects.count(),
            "today": checkins_today.count(),
            "safe": checkins_today.filter(status="safe").count(),
            "need_assistance": checkins_today.filter(status="need_assistance").count(),
        }

        return hazard_breakdown, checkins

    def list_urgent_flags(
        self, category=None, status=None, period=None, severity=None, hours=None
    ):
        qs = Hazard.objects.select_related("reporter").all()

        if category:
            qs = qs.filter(category=category)
        if status:
            qs = qs.filter(status=status)
        if period:
            qs = qs.filter(period=period)
        if severity:
            qs = qs.filter(severity=severity)
        if hours:
            cutoff = timezone.now() - timedelta(hours=int(hours))
            qs = qs.filter(created_at__gte=cutoff)

        return qs.order_by("-severity", "-created_at")
