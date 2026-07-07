from django.urls import path

from . import views

urlpatterns = [
    path("devices/register/", views.DeviceRegisterView.as_view(), name="device-register"),
    path("devices/unregister/", views.DeviceUnregisterView.as_view(), name="device-unregister"),
    path("notifications/", views.NotificationListView.as_view(), name="notification-list"),
    path(
        "notifications/<int:notification_id>/read/",
        views.NotificationReadView.as_view(),
        name="notification-read",
    ),
    path(
        "notifications/read-all/",
        views.NotificationReadAllView.as_view(),
        name="notification-read-all",
    ),
]
