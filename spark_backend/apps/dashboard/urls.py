from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/overview/", views.dashboard_overview_view, name="dashboard-overview"),
    path("dashboard/map/", views.dashboard_map_view, name="dashboard-map"),
    path("dashboard/reports/", views.dashboard_reports_view, name="dashboard-reports"),
]
