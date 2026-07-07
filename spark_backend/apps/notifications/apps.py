import os

from django.apps import AppConfig
from django.conf import settings


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
    label = "notifications"

    def ready(self):
        import firebase_admin
        from firebase_admin import credentials

        path = str(settings.FIREBASE_CREDENTIALS_PATH)
        if not os.path.exists(path):
            return
        if not firebase_admin._apps:
            cred = credentials.Certificate(path)
            firebase_admin.initialize_app(cred)
