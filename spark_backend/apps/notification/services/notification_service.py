import logging

from django.contrib.auth import get_user_model

from apps.comms.models import Notification as InAppNotification
from apps.notification.models import Notification
from apps.notification.tasks import send_push_notification

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationService:
    @staticmethod
    def send_notification(user, title, message, notification_types=None, data=None):
        if notification_types is None:
            notification_types = ["push"]
        if isinstance(user, str):
            user = User.objects.get(pk=user)

        preferences = getattr(user, "notification_preference", None)

        for notif_type in notification_types:
            if not NotificationService._should_send(user, notif_type, preferences):
                continue
            NotificationService._dispatch_notification(
                user, title, message, notif_type, data
            )

    @staticmethod
    def send_hub_notification(hub, title, message, notification_types=None, data=None):
        for user in hub.residents.all():
            NotificationService.send_notification(
                user, title, message, notification_types, data
            )

    @staticmethod
    def send_coordinator_notification(hub, title, message, notification_types=None, data=None):
        users = []
        if hub.coordinator:
            users.append(hub.coordinator)
        admins = (
            User.objects.filter(role="admin")
            .exclude(phone_number=hub.coordinator.phone_number if hub.coordinator else "")
            .distinct()
        )
        users.extend(admins)
        for user in users:
            NotificationService.send_notification(
                user, title, message, notification_types, data
            )

    @staticmethod
    def _should_send(user, notif_type, preferences):
        if not preferences:
            return True
        return getattr(preferences, f"{notif_type}_enabled", True)

    @staticmethod
    def _dispatch_notification(user, title, message, notif_type, data):
        record = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notif_type,
            data=data or {},
        )
        from apps.comms.models import Notification as InAppNotification
        InAppNotification.objects.create(
            user=user,
            type="alert",
            title=title,
            body=message,
            link=data.get("link") if data else None,
        )
        if notif_type == "push":
            try:
                send_push_notification.delay(record.id)
            except Exception:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning("Celery/Redis unavailable; push skipped (in-app notification saved)")
