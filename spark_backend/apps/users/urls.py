from django.urls import path

from . import views

urlpatterns = [
    # Resident OTP Flow
    path("auth/register/", views.register_view, name="auth-register"),
    path("auth/otp/send/", views.otp_send_view, name="auth-otp-send"),
    path("auth/otp/verify/", views.otp_verify_view, name="auth-otp-verify"),
    # Email/Password Login
    path("auth/login/", views.login_view, name="auth-login"),
    path("auth/logout/", views.logout_view, name="auth-logout"),
    path("auth/refresh/", views.BlacklistCheckTokenRefreshView.as_view(), name="auth-refresh"),
    # Biometric
    path("auth/biometric/register/", views.biometric_register_view, name="auth-biometric-register"),
    path("auth/biometric/login/", views.biometric_login_view, name="auth-biometric-login"),
    # Offline Token
    path("auth/offline-token/", views.offline_token_view, name="auth-offline-token"),
    # Government Invite (exact paths BEFORE <str:token>)
    path("auth/invite/accept/", views.invite_accept_view, name="auth-invite-accept"),
    path("auth/invite/<str:token>/", views.invite_validate_view, name="auth-invite-validate"),
    # Password Reset
    path("auth/forgot-password/", views.forgot_password_view, name="auth-forgot-password"),
    path("auth/reset-password/", views.reset_password_view, name="auth-reset-password"),
    # Profile
    path("users/profile/", views.profile_view, name="users-profile"),
    path("users/change-password/", views.change_password_view, name="users-change-password"),
    # Admin
    path("admin/users/invite/", views.invite_government_view, name="admin-users-invite"),
    path("admin/users/<str:user_id>/set-role/", views.set_role_view, name="admin-users-set-role"),
]
