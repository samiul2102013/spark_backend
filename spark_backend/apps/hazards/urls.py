from django.urls import path

from . import views

urlpatterns = [
    path("hazards/", views.HazardListView.as_view(), name="hazard-list"),
    path("hazards/<int:hazard_id>/", views.HazardDetailView.as_view(), name="hazard-detail"),
    path("hazards/<int:hazard_id>/clear/", views.HazardClearView.as_view(), name="hazard-clear"),
    path("hazards/<int:hazard_id>/comments/", views.HazardCommentListView.as_view(), name="hazard-comment-list"),
]
