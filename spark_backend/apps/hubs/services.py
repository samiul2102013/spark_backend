from django.contrib.auth import get_user_model
from django.db import transaction

from apps.bookings.models import Booking
from apps.comms.models import Broadcast, CheckIn
from core.exceptions import HubNotFoundError

from .models import Hub

User = get_user_model()


class HubService:
    def list_hubs(self, status=None):
        qs = Hub.objects.select_related("coordinator").all()
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_hub(self, hub_id):
        try:
            return Hub.objects.select_related("coordinator").get(pk=hub_id)
        except Hub.DoesNotExist:
            raise HubNotFoundError()

    @transaction.atomic
    def create_hub(self, data):
        coordinator_id = data.pop("coordinator", None)
        hub = Hub.objects.create(**data)
        if coordinator_id:
            try:
                coordinator = User.objects.get(phone_number=coordinator_id, role="coordinator")
                hub.coordinator = coordinator
                hub.save(update_fields=["coordinator"])
            except User.DoesNotExist:
                pass
        return hub

    @transaction.atomic
    def update_hub(self, hub_id, data):
        hub = self.get_hub(hub_id)
        for field, value in data.items():
            setattr(hub, field, value)
        hub.save()
        return hub

    @transaction.atomic
    def delete_hub(self, hub_id):
        hub = self.get_hub(hub_id)
        hub.delete()

    @transaction.atomic
    def update_status(self, hub_id, status, extra=None):
        hub = self.get_hub(hub_id)
        hub.status = status
        if extra:
            for field, value in extra.items():
                if hasattr(hub, field):
                    setattr(hub, field, value)
        hub.save()
        return hub

    @transaction.atomic
    def assign_coordinator(self, hub_id, coordinator_id):
        hub = self.get_hub(hub_id)
        try:
            coordinator = User.objects.get(phone_number=coordinator_id)
        except User.DoesNotExist:
            raise HubNotFoundError("Coordinator not found.")
        hub.coordinator = coordinator
        hub.save(update_fields=["coordinator"])
        return hub

    def get_hub_checkins(self, hub_id, date=None):
        qs = CheckIn.objects.filter(hub_id=hub_id).select_related("user")
        if date:
            qs = qs.filter(timestamp__date=date)
        return qs.order_by("-timestamp")

    def get_hub_broadcasts(self, hub_id):
        return Broadcast.objects.filter(hub_id=hub_id).order_by("-created_at")

    def get_hub_resources(self, hub_id):
        hub = self.get_hub(hub_id)
        active_bookings = Booking.objects.filter(hub=hub, status="active").count()
        return {
            "battery_percentage": hub.battery_percentage,
            "solar_input_w": hub.solar_input_w,
            "solar_output_w": hub.solar_output_w,
            "estimated_runtime_h": hub.estimated_runtime_h,
            "starlink_status": hub.starlink_status,
            "active_bookings": active_bookings,
        }
