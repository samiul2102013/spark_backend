from django.urls import path

from . import views as admin_views

urlpatterns = [
    # Overview
    path("admin/overview/", admin_views.AdminOverviewView.as_view(), name="admin-overview"),
    # Residents
    path(
        "admin/residents/", admin_views.AdminResidentListView.as_view(), name="admin-resident-list"
    ),
    path(
        "admin/residents/<int:user_id>/",
        admin_views.AdminResidentDetailView.as_view(),
        name="admin-resident-detail",
    ),
    path(
        "admin/residents/<int:user_id>/suspend/",
        admin_views.AdminResidentSuspendView.as_view(),
        name="admin-resident-suspend",
    ),
    path(
        "admin/residents/<int:user_id>/activate/",
        admin_views.AdminResidentActivateView.as_view(),
        name="admin-resident-activate",
    ),
    # Coordinators
    path(
        "admin/coordinators/",
        admin_views.AdminCoordinatorListView.as_view(),
        name="admin-coordinator-list",
    ),
    path(
        "admin/coordinators/<int:user_id>/",
        admin_views.AdminCoordinatorDetailView.as_view(),
        name="admin-coordinator-detail",
    ),
    path(
        "admin/coordinators/<int:user_id>/suspend/",
        admin_views.AdminCoordinatorSuspendView.as_view(),
        name="admin-coordinator-suspend",
    ),
    # Users (invite + role)
    path(
        "admin/users/invite/", admin_views.AdminInviteUserView.as_view(), name="admin-users-invite"
    ),
    path(
        "admin/users/<int:user_id>/role/",
        admin_views.AdminSetRoleView.as_view(),
        name="admin-users-set-role",
    ),
    # Hubs
    path("admin/hubs/", admin_views.AdminHubListView.as_view(), name="admin-hub-list"),
    path(
        "admin/hubs/<int:hub_id>/",
        admin_views.AdminHubDetailView.as_view(),
        name="admin-hub-detail",
    ),
    path("admin/hubs/create/", admin_views.AdminHubCreateView.as_view(), name="admin-hub-create"),
    path(
        "admin/hubs/<int:hub_id>/assign-coordinator/",
        admin_views.AdminHubAssignCoordinatorView.as_view(),
        name="admin-hub-assign-coordinator",
    ),
    path(
        "admin/hubs/<int:hub_id>/reassign-coordinator/",
        admin_views.AdminHubReassignCoordinatorView.as_view(),
        name="admin-hub-reassign-coordinator",
    ),
    # Reports & AI
    path("admin/reports/", admin_views.AdminReportListView.as_view(), name="admin-report-list"),
    path(
        "admin/reports/<int:report_id>/",
        admin_views.AdminReportDetailView.as_view(),
        name="admin-report-detail",
    ),
    path("admin/ai-config/", admin_views.AdminAIConfigView.as_view(), name="admin-ai-config"),
    # Messages
    path("admin/messages/", admin_views.AdminMessageListView.as_view(), name="admin-message-list"),
    path(
        "admin/messages/<int:msg_id>/",
        admin_views.AdminMessageDetailView.as_view(),
        name="admin-message-detail",
    ),
    path(
        "admin/messages/<int:msg_id>/classify/",
        admin_views.AdminMessageClassifyView.as_view(),
        name="admin-message-classify",
    ),
]
