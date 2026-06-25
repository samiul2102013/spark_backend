from django.urls import path

from . import views

urlpatterns = [
    path("gov/overview/", views.GovOverviewView.as_view(), name="gov-overview"),
    path("gov/map/", views.GovMapView.as_view(), name="gov-map"),
    path("gov/hazards/<int:hazard_id>/", views.GovHazardDetailView.as_view(), name="gov-hazard-detail"),
    path("gov/reports/", views.GovReportsView.as_view(), name="gov-reports"),
    path("gov/infrastructure/", views.GovInfrastructureView.as_view(), name="gov-infrastructure"),
    path("gov/infrastructure/<int:hub_id>/", views.GovInfrastructureDetailView.as_view(), name="gov-infrastructure-detail"),
]
