from django.db import transaction

from apps.notification.services.notification_service import NotificationService as PushNotificationService

from .models import Broadcast, BroadcastRead, CheckIn


class CheckInService:
    def list_checkins(self, hub_id=None, user=None, status=None, date=None):
        qs = CheckIn.objects.select_related("user", "hub").all()
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        if user:
            qs = qs.filter(user=user)
        if status:
            qs = qs.filter(status=status)
        if date:
            qs = qs.filter(timestamp__date=date)
        return qs.order_by("-timestamp")

    @transaction.atomic
    def create_checkin(self, data, user=None):
        if user:
            data["user"] = user
        hub_id = data.pop("hub")
        data["hub_id"] = hub_id
        checkin = CheckIn.objects.create(**data)
        if checkin.help_description:
            from apps.ai.services import AIScoringService
            checkin.risk_score = AIScoringService.assign_risk_score(
                checkin.help_description, category=None
            )
            if checkin.risk_score is not None:
                checkin.save(update_fields=["risk_score"])
        if checkin.status == "need_assistance" and checkin.hub:
            PushNotificationService.send_coordinator_notification(
                hub=checkin.hub,
                title="Assistance Needed",
                message=f"{checkin.user.full_name or checkin.user.phone_number} needs help at {checkin.hub.name}: {checkin.get_assistance_type_display() or 'Assistance requested'}",
                data={"checkin_id": str(checkin.id), "status": "need_assistance"},
            )
        return checkin

    def get_latest_checkin(self, user):
        return CheckIn.objects.filter(user=user).order_by("-timestamp").first()

    def get_checkin(self, checkin_id):
        return CheckIn.objects.select_related("user", "hub").get(id=checkin_id)


class BroadcastService:
    def list_broadcasts(self, hub_id=None):
        qs = Broadcast.objects.select_related("hub", "sender").all()
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        return qs.order_by("-created_at")

    @transaction.atomic
    def create_broadcast(self, hub_id, data, sender=None):
        if sender:
            data["sender"] = sender
        data["hub_id"] = hub_id
        broadcast = Broadcast.objects.create(**data)
        if broadcast.priority in ("warning", "urgent"):
            PushNotificationService.send_hub_notification(
                hub=broadcast.hub,
                title=f"{broadcast.priority.upper()} Broadcast",
                message=f"{broadcast.subject}: {broadcast.body[:100]}",
                data={"broadcast_id": str(broadcast.id), "priority": broadcast.priority},
            )
        return broadcast

    @transaction.atomic
    def mark_read(self, broadcast_id, user):
        obj, _ = BroadcastRead.objects.get_or_create(broadcast_id=broadcast_id, user=user)
        return obj

    @transaction.atomic
    def delete_broadcast(self, broadcast_id, user):
        broadcast = Broadcast.objects.select_related("hub").get(id=broadcast_id)
        if user.role != "admin" and broadcast.hub_id != getattr(user.hub, "id", None):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete broadcasts from your own hub.")
        broadcast.delete()
        return broadcast
