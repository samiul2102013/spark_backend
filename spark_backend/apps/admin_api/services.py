from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from apps.bookings.models import Booking
from apps.comms.models import CheckIn, InboundMessage
from apps.hazards.models import Hazard
from apps.hubs.models import Hub
from apps.users.models import User


class AdminOverviewService:
    def overview(self):
        today = timezone.now().date()
        now = timezone.now()
        twenty_four_hours_ago = now - timedelta(hours=24)

        users = User.objects.all()
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
            "users": {
                "total": users.count(),
                "residents": users.filter(role="resident").count(),
                "coordinators": users.filter(role="coordinator").count(),
                "active": users.filter(is_active=True).count(),
            },
            "messages": {
                "inbound_today": InboundMessage.objects.filter(
                    created_at__date=today
                ).count(),
                "unclassified": InboundMessage.objects.filter(
                    status="unclassified"
                ).count(),
            },
        }


class AdminUserService:
    def list_residents(self, hub_id=None, is_active=None, search=None):
        qs = User.objects.filter(role="resident")
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search)
                | Q(phone_number__icontains=search)
                | Q(email__icontains=search)
            )
        return qs

    def get_resident(self, user_id):
        return User.objects.get(phone_number=user_id, role="resident")

    def list_coordinators(self, hub_id=None, is_active=None, search=None):
        qs = User.objects.filter(role="coordinator")
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search)
                | Q(phone_number__icontains=search)
                | Q(email__icontains=search)
            )
        return qs

    def get_coordinator(self, user_id):
        return User.objects.get(phone_number=user_id, role="coordinator")

    def list_all_users(self, role=None, is_active=None, search=None):
        qs = User.objects.all()
        if role:
            qs = qs.filter(role=role)
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search)
                | Q(phone_number__icontains=search)
                | Q(email__icontains=search)
            )
        return qs

    def suspend_user(self, user_id):
        user = User.objects.get(phone_number=user_id)
        user.is_active = False
        user.save(update_fields=["is_active"])
        return user

    def activate_user(self, user_id):
        user = User.objects.get(phone_number=user_id)
        user.is_active = True
        user.save(update_fields=["is_active"])
        return user

    def invite_user(self, data):
        phone = data.get("phone_number")
        user = User.objects.filter(phone_number=phone).first()
        if user:
            user.full_name = data.get("full_name", user.full_name)
            user.role = data.get("role", user.role)
            user.hub_id = data.get("hub_id", user.hub_id)
            user.is_active = True
            user.save()
            return user

        user = User.objects.create_user(
            phone_number=phone,
            full_name=data["full_name"],
            role=data["role"],
            hub_id=data.get("hub_id"),
            is_active=True,
        )
        return user

    def set_role(self, user_id, role):
        user = User.objects.get(phone_number=user_id)
        if role not in ("resident", "coordinator", "government", "admin"):
            raise ValueError("Invalid role.")
        user.role = role
        user.save(update_fields=["role"])
        return user


class AdminHubService:
    def list_hubs(self, status=None, search=None):
        qs = Hub.objects.select_related("coordinator").all()
        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(address__icontains=search))
        return qs

    def get_hub(self, hub_id):
        return Hub.objects.select_related("coordinator").get(id=hub_id)

    def create_hub(self, data):
        coordinator_id = data.pop("coordinator_id", None)
        hub = Hub.objects.create(**data)
        if coordinator_id:
            try:
                coord = User.objects.get(phone_number=coordinator_id, role="coordinator")
                hub.coordinator = coord
                hub.save(update_fields=["coordinator"])
            except User.DoesNotExist:
                pass
        return hub

    def assign_coordinator(self, hub_id, coordinator_id):
        hub = Hub.objects.get(id=hub_id)
        coord = User.objects.get(phone_number=coordinator_id)
        hub.coordinator = coord
        hub.save(update_fields=["coordinator"])
        return hub

    def reassign_coordinator(self, hub_id, new_coordinator_id):
        hub = Hub.objects.get(id=hub_id)
        coord = User.objects.get(phone_number=new_coordinator_id)
        hub.coordinator = coord
        hub.save(update_fields=["coordinator"])
        return hub

    def update_hub(self, hub_id, data):
        hub = Hub.objects.get(id=hub_id)
        for field, value in data.items():
            setattr(hub, field, value)
        hub.save()
        return hub
