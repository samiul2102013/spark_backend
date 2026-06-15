from django.urls import path

from . import views

urlpatterns = [
    path("checkins/", views.checkin_list_view, name="checkin-list"),
    path("checkins/create/", views.checkin_create_view, name="checkin-create"),
    path("broadcasts/", views.broadcast_list_view, name="broadcast-list"),
    path("broadcasts/create/", views.broadcast_create_view, name="broadcast-create"),
    path(
        "broadcasts/<int:broadcast_id>/read/",
        views.broadcast_mark_read_view,
        name="broadcast-mark-read",
    ),
    path("notifications/", views.notification_list_view, name="notification-list"),
    path(
        "notifications/<int:notification_id>/read/",
        views.notification_mark_read_view,
        name="notification-mark-read",
    ),
]
