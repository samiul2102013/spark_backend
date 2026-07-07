from django.db import transaction

from apps.notifications.services import NotificationOrchestrator

from .models import Broadcast, BroadcastRead, CheckIn, Notification


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
            NotificationOrchestrator.notify_coordinators_and_admins(
                hub=checkin.hub,
                type="alert",
                title="Assistance Needed",
                body=f"{checkin.user.full_name or checkin.user.phone_number} needs help at {checkin.hub.name}: {checkin.get_assistance_type_display() or 'Assistance requested'}",
                link=f"/checkins/{checkin.id}",
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
            NotificationOrchestrator.notify_hub_users(
                hub=broadcast.hub,
                type="broadcast",
                title=f"{broadcast.priority.upper()} Broadcast",
                body=f"{broadcast.subject}: {broadcast.body[:100]}",
                link=f"/broadcasts/{broadcast.id}",
                data={"broadcast_id": str(broadcast.id), "priority": broadcast.priority},
            )
        return broadcast

    @transaction.atomic
    def mark_read(self, broadcast_id, user):
        obj, _ = BroadcastRead.objects.get_or_create(broadcast_id=broadcast_id, user=user)
        return obj


class NotificationService:
    def list_notifications(self, user, unread_only=False):
        qs = Notification.objects.filter(user=user).select_related("hub")
        if unread_only:
            qs = qs.filter(read=False)
        return qs.order_by("-created_at")

    @transaction.atomic
    def mark_read(self, notification_id, user):
        notification = Notification.objects.get(id=notification_id, user=user)
        notification.read = True
        notification.save(update_fields=["read"])
        return notification

    @transaction.atomic
    def mark_all_read(self, user):
        updated = Notification.objects.filter(user=user, read=False).update(read=True)
        return {"marked_read": updated}

    @transaction.atomic
    def create_notification(self, user, type, title, body, hub=None, link=None):
        return Notification.objects.create(
            user=user, type=type, title=title, body=body, hub=hub, link=link
        )
