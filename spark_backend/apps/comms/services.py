from django.db import transaction

from .models import Broadcast, BroadcastRead, CheckIn, Notification


class CheckInService:
    @staticmethod
    def list_checkins(hub_id=None, user=None):
        qs = CheckIn.objects.select_related("user", "hub").all()
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        if user:
            qs = qs.filter(user=user)
        return qs

    @staticmethod
    @transaction.atomic
    def create_checkin(data, user=None):
        if user:
            data["user"] = user
        return CheckIn.objects.create(**data)


class BroadcastService:
    @staticmethod
    def list_broadcasts(hub_id=None):
        qs = Broadcast.objects.select_related("hub", "sender").all()
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        return qs

    @staticmethod
    @transaction.atomic
    def create_broadcast(data, sender=None):
        if sender:
            data["sender"] = sender
        return Broadcast.objects.create(**data)


class BroadcastReadService:
    @staticmethod
    @transaction.atomic
    def mark_read(broadcast_id, user):
        obj, _ = BroadcastRead.objects.get_or_create(broadcast_id=broadcast_id, user=user)
        return obj


class NotificationService:
    @staticmethod
    def list_notifications(user, unread_only=False):
        qs = Notification.objects.filter(user=user).select_related("hub")
        if unread_only:
            qs = qs.filter(read=False)
        return qs

    @staticmethod
    @transaction.atomic
    def mark_read(notification_id, user):
        notification = Notification.objects.get(id=notification_id, user=user)
        notification.read = True
        notification.save()
        return notification

    @staticmethod
    @transaction.atomic
    def create_notification(user, type, title, body, hub=None, link=None):
        return Notification.objects.create(
            user=user, type=type, title=title, body=body, hub=hub, link=link
        )
