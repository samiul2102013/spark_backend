from django.urls import path

from . import views

urlpatterns = [
    path("hubs/nearest/", views.NearestHubView.as_view(), name="hub-nearest"),
    path("hubs/", views.HubListView.as_view(), name="hub-list"),
    path("hubs/<int:hub_id>/", views.HubDetailView.as_view(), name="hub-detail"),
    path("hubs/<int:hub_id>/status/", views.HubStatusView.as_view(), name="hub-status-update"),
    path(
        "hubs/<int:hub_id>/coordinator/", views.HubCoordinatorView.as_view(), name="hub-coordinator"
    ),
    path("hubs/<int:hub_id>/slots/", views.HubSlotsDetailView.as_view(), name="hub-slots"),
    path("hubs/<int:hub_id>/checkins/", views.HubCheckinsView.as_view(), name="hub-checkins"),
    path("hubs/<int:hub_id>/broadcasts/", views.HubBroadcastsView.as_view(), name="hub-broadcasts"),
    path("hubs/<int:hub_id>/resources/", views.HubResourcesView.as_view(), name="hub-resources"),
]
