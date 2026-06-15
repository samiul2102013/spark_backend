from django.urls import path

from . import views

urlpatterns = [
    path("hazards/", views.hazard_list_view, name="hazard-list"),
    path("hazards/<int:hazard_id>/", views.hazard_detail_view, name="hazard-detail"),
    path("hazards/create/", views.hazard_create_view, name="hazard-create"),
    path("hazards/<int:hazard_id>/update/", views.hazard_update_view, name="hazard-update"),
    path("hazards/<int:hazard_id>/delete/", views.hazard_delete_view, name="hazard-delete"),
    path(
        "hazards/<int:hazard_id>/comments/",
        views.hazard_comment_list_view,
        name="hazard-comment-list",
    ),
    path(
        "hazards/<int:hazard_id>/comments/create/",
        views.hazard_comment_create_view,
        name="hazard-comment-create",
    ),
]
