from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/urgent-flags/", views.UrgentFlagsView.as_view(), name="dashboard-urgent-flags"),
]
