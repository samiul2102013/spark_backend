from django.urls import path

from . import views

urlpatterns = [
    # Overview
    path("admin/overview/", views.AdminOverviewView.as_view(), name="admin-overview"),
    # Residents
    path("admin/residents/", views.AdminResidentListView.as_view(), name="admin-resident-list"),
    path(
        "admin/residents/<str:user_id>/",
        views.AdminResidentDetailView.as_view(),
        name="admin-resident-detail",
    ),
    path(
        "admin/residents/<str:user_id>/suspend/",
        views.AdminResidentSuspendView.as_view(),
        name="admin-resident-suspend",
    ),
    path(
        "admin/residents/<str:user_id>/activate/",
        views.AdminResidentActivateView.as_view(),
        name="admin-resident-activate",
    ),
    # Coordinators
    path(
        "admin/coordinators/",
        views.AdminCoordinatorListView.as_view(),
        name="admin-coordinator-list",
    ),
    path(
        "admin/coordinators/<str:user_id>/",
        views.AdminCoordinatorDetailView.as_view(),
        name="admin-coordinator-detail",
    ),
    path(
        "admin/coordinators/<str:user_id>/suspend/",
        views.AdminCoordinatorSuspendView.as_view(),
        name="admin-coordinator-suspend",
    ),
    # Users (access control)
    path("admin/users/", views.AdminUserListView.as_view(), name="admin-user-list"),
    path(
        "admin/users/<str:user_id>/suspend/",
        views.AdminUserSuspendView.as_view(),
        name="admin-user-suspend",
    ),
    path(
        "admin/users/<str:user_id>/activate/",
        views.AdminUserActivateView.as_view(),
        name="admin-user-activate",
    ),
    path(
        "admin/users/invite/", views.AdminInviteUserView.as_view(), name="admin-users-invite"
    ),
    path(
        "admin/users/invite-by-email/",
        views.AdminInviteByEmailView.as_view(),
        name="admin-users-invite-by-email",
    ),
    path(
        "admin/users/<str:user_id>/role/",
        views.AdminSetRoleView.as_view(),
        name="admin-users-set-role",
    ),
    # Hubs
    path("admin/hubs/", views.AdminHubListView.as_view(), name="admin-hub-list"),
    path("admin/hubs/<int:hub_id>/", views.AdminHubDetailView.as_view(), name="admin-hub-detail"),
    path("admin/hubs/create/", views.AdminHubCreateView.as_view(), name="admin-hub-create"),
    path(
        "admin/hubs/<int:hub_id>/assign-coordinator/",
        views.AdminHubAssignCoordinatorView.as_view(),
        name="admin-hub-assign-coordinator",
    ),
    path(
        "admin/hubs/<int:hub_id>/reassign-coordinator/",
        views.AdminHubReassignCoordinatorView.as_view(),
        name="admin-hub-reassign-coordinator",
    ),
    # Admin Profile & Security
    path("admin/profile/", views.AdminProfileView.as_view(), name="admin-profile"),
    path(
        "admin/change-password/",
        views.AdminChangePasswordView.as_view(),
        name="admin-change-password",
    ),
]
