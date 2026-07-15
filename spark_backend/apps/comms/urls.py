from django.urls import path

from . import views

urlpatterns = [
    path("checkins/", views.CheckInView.as_view(), name="checkin-create"),
    path("checkins/history/", views.CheckInHistoryView.as_view(), name="checkin-history"),
    path("checkins/latest/", views.CheckInLatestView.as_view(), name="checkin-latest"),
    path("checkins/<int:checkin_id>/", views.CheckInDetailView.as_view(), name="checkin-detail"),
    path("broadcasts/", views.BroadcastListView.as_view(), name="broadcast-list"),
    path("broadcasts/create/", views.BroadcastCreateView.as_view(), name="broadcast-create"),
    path(
        "broadcasts/<int:broadcast_id>/read/",
        views.BroadcastReadView.as_view(),
        name="broadcast-read",
    ),
    path(
        "broadcasts/<int:broadcast_id>/delete/",
        views.BroadcastDeleteView.as_view(),
        name="broadcast-delete",
    ),
]
