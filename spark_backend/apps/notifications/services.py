from firebase_admin import messaging

from apps.comms.models import Notification


class FCMService:
    @staticmethod
    def send_push(user, title, body, data=None):
        tokens = list(user.device_tokens.values_list("token", flat=True))
        if not tokens:
            return
        FCMService.send_push_to_tokens(tokens, title, body, data)

    @staticmethod
    def send_push_to_tokens(tokens, title, body, data=None):
        if not tokens:
            return
        message = messaging.MulticastMessage(
            tokens=tokens,
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
        )
        messaging.send_each_for_multicast(message)

    @staticmethod
    def send_push_to_hub_users(hub, title, body, data=None):
        users = hub.residents.all()
        for user in users:
            FCMService.send_push(user, title, body, data)

    @staticmethod
    def send_push_to_hub_coordinators(hub, title, body, data=None):
        if hub.coordinator:
            FCMService.send_push(hub.coordinator, title, body, data)
        admins = (
            hub.residents.model.objects.filter(role="admin")
            .exclude(phone_number=hub.coordinator.phone_number if hub.coordinator else "")
            .distinct()
        )
        for admin in admins:
            FCMService.send_push(admin, title, body, data)


class NotificationOrchestrator:
    @staticmethod
    def notify(user, type, title, body, hub=None, link=None, data=None):
        Notification.objects.create(
            user=user, type=type, title=title, body=body, hub=hub, link=link
        )
        FCMService.send_push(user, title, body, data)

    @staticmethod
    def notify_hub_users(hub, type, title, body, link=None, data=None):
        for user in hub.residents.all():
            NotificationOrchestrator.notify(user, type, title, body, hub=hub, link=link, data=data)

    @staticmethod
    def notify_coordinators_and_admins(hub, type, title, body, link=None, data=None):
        users = []
        if hub.coordinator:
            users.append(hub.coordinator)
        admins = (
            hub.residents.model.objects.filter(role="admin")
            .exclude(phone_number=hub.coordinator.phone_number if hub.coordinator else "")
            .distinct()
        )
        users.extend(admins)
        for user in users:
            NotificationOrchestrator.notify(
                user, type, title, body, hub=hub, link=link, data=data
            )
