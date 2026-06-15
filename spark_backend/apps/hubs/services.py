from django.contrib.auth import get_user_model
from django.db import transaction

from core.exceptions import HubNotFoundError

from .models import Hub

User = get_user_model()


class HubService:

    @staticmethod
    def list_hubs(status: str = None) -> list:
        qs = Hub.objects.select_related("coordinator").all()
        if status:
            qs = qs.filter(status=status)
        return qs

    @staticmethod
    def get_hub(hub_id: int) -> Hub:
        try:
            return Hub.objects.select_related("coordinator").get(pk=hub_id)
        except Hub.DoesNotExist:
            raise HubNotFoundError()

    @staticmethod
    @transaction.atomic
    def create_hub(data: dict) -> Hub:
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

    @staticmethod
    @transaction.atomic
    def update_hub(hub_id: int, data: dict) -> Hub:
        hub = HubService.get_hub(hub_id)
        for field, value in data.items():
            setattr(hub, field, value)
        hub.save()
        return hub

    @staticmethod
    @transaction.atomic
    def delete_hub(hub_id: int) -> None:
        hub = HubService.get_hub(hub_id)
        hub.delete()

    @staticmethod
    @transaction.atomic
    def update_status(hub_id: int, status: str, extra: dict = None) -> Hub:
        hub = HubService.get_hub(hub_id)
        hub.status = status
        if extra:
            for field, value in extra.items():
                if hasattr(hub, field):
                    setattr(hub, field, value)
        hub.save()
        return hub

    @staticmethod
    @transaction.atomic
    def assign_coordinator(hub_id: int, coordinator_id: str) -> Hub:
        hub = HubService.get_hub(hub_id)
        try:
            coordinator = User.objects.get(phone_number=coordinator_id)
        except User.DoesNotExist:
            raise HubNotFoundError("Coordinator not found.")
        hub.coordinator = coordinator
        hub.save(update_fields=["coordinator"])
        return hub
