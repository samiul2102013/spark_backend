import logging
import os

import firebase_admin
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from firebase_admin import credentials, messaging

logger = logging.getLogger(__name__)

path = str(settings.FIREBASE_CREDENTIALS_PATH)
if os.path.exists(path) and not firebase_admin._apps:
    cred = credentials.Certificate(path)
    firebase_admin.initialize_app(cred)


@shared_task(bind=True, max_retries=3)
def send_push_notification(self, notification_id):
    try:
        from .models import FCMToken, Notification

        notification = Notification.objects.get(id=notification_id)
        tokens = FCMToken.objects.filter(
            user=notification.user,
            is_active=True,
        ).values_list("token", flat=True)

        if not tokens:
            logger.warning(f"No active FCM tokens for user {notification.user.phone_number}")
            return

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=notification.title,
                body=notification.message,
            ),
            data={str(k): str(v) for k, v in notification.data.items()} if notification.data else {
                "type": "notification",
            },
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        alert=messaging.ApsAlert(
                            title=notification.title,
                            body=notification.message,
                        ),
                        badge=1,
                        sound="default",
                        content_available=True,
                    )
                ),
                headers={
                    "apns-priority": "10",
                    "apns-push-type": "alert",
                },
            ),
            tokens=list(tokens),
        )

        response = messaging.send_each_for_multicast(message)
        logger.info(
            f"Push: {response.success_count} success, {response.failure_count} failures"
        )

        if response.failure_count > 0:
            _handle_failed_tokens(response, list(tokens), notification.user)

        notification.sent_at = timezone.now()
        notification.save()

    except Exception as exc:
        logger.error(f"Push notification error: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


def _handle_failed_tokens(response, tokens, user):
    from .models import FCMToken

    if response.failure_count > 0:
        failed_tokens = []
        for idx, resp in enumerate(response.responses):
            if not resp.success:
                failed_tokens.append(tokens[idx])

        FCMToken.objects.filter(user=user, token__in=failed_tokens).update(is_active=False)
