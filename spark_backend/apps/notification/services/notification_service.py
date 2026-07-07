import logging

from django.contrib.auth import get_user_model

from apps.notification.models import Notification
from apps.notification.tasks import send_push_notification

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationService:

    CATEGORY_MAP = {
        "alert": "alert",
        "broadcast": "broadcast",
        "booking": "booking",
        "hub_status": "hub_status",
    }

    @staticmethod
    def send_notification(user, title, message, category="alert", data=None, link=None, hub=None, send_push=False):
        if isinstance(user, str):
            user = User.objects.get(pk=user)

        record = Notification.objects.create(
            user=user,
            hub=hub,
            title=title,
            message=message,
            category=category,
            data=data or {},
            link=link,
        )

        if send_push:
            try:
                send_push_notification.delay(record.id)
            except Exception:
                logger.warning("Celery/Redis unavailable; push skipped (in-app notification saved)")

        return record

    @staticmethod
    def send_hub_notification(hub, title, message, category="alert", data=None, link=None):
        notifications = []
        for user in hub.residents.all():
            n = NotificationService.send_notification(
                user, title, message, category=category, data=data, link=link, hub=hub, send_push=True
            )
            notifications.append(n)
        return notifications

    @staticmethod
    def send_coordinator_notification(hub, title, message, category="alert", data=None, link=None):
        users = []
        if hub.coordinator:
            users.append(hub.coordinator)
        admins = (
            User.objects.filter(role="admin")
            .exclude(phone_number=hub.coordinator.phone_number if hub.coordinator else "")
            .distinct()
        )
        users.extend(admins)
        notifications = []
        for user in users:
            n = NotificationService.send_notification(
                user, title, message, category=category, data=data, link=link, hub=hub, send_push=True
            )
            notifications.append(n)
        return notifications

    @staticmethod
    def list_notifications(user, unread_only=False):
        qs = Notification.objects.filter(user=user).select_related("hub")
        if unread_only:
            qs = qs.filter(read=False)
        return qs.order_by("-created_at")

    @staticmethod
    def mark_read(notification_id, user):
        notification = Notification.objects.get(id=notification_id, user=user)
        notification.read = True
        notification.save(update_fields=["read"])
        return notification

    @staticmethod
    def mark_all_read(user):
        updated = Notification.objects.filter(user=user, read=False).update(read=True)
        return {"marked_read": updated}
