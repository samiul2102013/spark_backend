from django.urls import path

from . import views

urlpatterns = [
    path("checkins/", views.CheckInView.as_view(), name="checkin-create"),
    path("checkins/history/", views.CheckInHistoryView.as_view(), name="checkin-history"),
    path("checkins/latest/", views.CheckInLatestView.as_view(), name="checkin-latest"),
    path("broadcasts/", views.BroadcastListView.as_view(), name="broadcast-list"),
    path("broadcasts/create/", views.BroadcastCreateView.as_view(), name="broadcast-create"),
    path("broadcasts/<int:broadcast_id>/read/", views.BroadcastReadView.as_view(), name="broadcast-read"),
    path("notifications/", views.NotificationListView.as_view(), name="notification-list"),
    path("notifications/<int:notification_id>/read/", views.NotificationReadView.as_view(), name="notification-read"),
    path("notifications/read-all/", views.NotificationReadAllView.as_view(), name="notification-read-all"),
]
