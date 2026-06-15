from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/overview/", views.DashboardOverviewView.as_view(), name="dashboard-overview"),
    path("dashboard/map/", views.DashboardMapView.as_view(), name="dashboard-map"),
    path("dashboard/reports/", views.DashboardReportsView.as_view(), name="dashboard-reports"),
    path("dashboard/alerts/", views.DashboardAlertsView.as_view(), name="dashboard-alerts"),
    path("dashboard/infrastructure/", views.DashboardInfrastructureView.as_view(), name="dashboard-infrastructure"),
    path("dashboard/infrastructure/<int:hub_id>/", views.DashboardInfrastructureDetailView.as_view(), name="dashboard-infrastructure-detail"),
]
