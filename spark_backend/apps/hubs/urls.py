from django.urls import path

from . import views

urlpatterns = [
    path("hubs/", views.hub_list_view, name="hub-list"),
    path("hubs/<int:hub_id>/", views.hub_detail_view, name="hub-detail"),
    path("hubs/create/", views.hub_create_view, name="hub-create"),
    path("hubs/<int:hub_id>/update/", views.hub_update_view, name="hub-update"),
    path("hubs/<int:hub_id>/delete/", views.hub_delete_view, name="hub-delete"),
    path("hubs/<int:hub_id>/status/", views.hub_status_update_view, name="hub-status-update"),
    path(
        "hubs/<int:hub_id>/assign-coordinator/",
        views.hub_assign_coordinator_view,
        name="hub-assign-coordinator",
    ),
]
