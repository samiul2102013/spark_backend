from django.urls import path

from . import views

urlpatterns = [
    # Resident OTP Flow
    path("auth/register/", views.RegisterView.as_view(), name="auth-register"),
    path("auth/otp/send/", views.OTPSendView.as_view(), name="auth-otp-send"),
    path("auth/otp/verify/", views.OTPVerifyView.as_view(), name="auth-otp-verify"),
    # Email/Password Login
    path("auth/login/", views.LoginView.as_view(), name="auth-login"),
    path("auth/logout/", views.LogoutView.as_view(), name="auth-logout"),
    path("auth/refresh/", views.BlacklistCheckTokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/set-password/", views.SetPasswordView.as_view(), name="auth-set-password"),
    # Biometric
    path(
        "auth/biometric/register/",
        views.BiometricRegisterView.as_view(),
        name="auth-biometric-register",
    ),
    path("auth/biometric/login/", views.BiometricLoginView.as_view(), name="auth-biometric-login"),
    # Apple Sign-In
    path("auth/apple/login/", views.AppleLoginView.as_view(), name="apple-login"),
    # Offline Token
    path("auth/offline-token/", views.OfflineTokenView.as_view(), name="auth-offline-token"),
    # Government Invite
    path("auth/invite/accept/", views.InviteAcceptView.as_view(), name="auth-invite-accept"),
    path(
        "auth/invite/<str:token>/", views.InviteValidateView.as_view(), name="auth-invite-validate"
    ),
    # Password Reset
    path("auth/forgot-password/", views.ForgotPasswordView.as_view(), name="auth-forgot-password"),
    path(
        "auth/verify-reset-otp/",
        views.VerifyResetOTPView.as_view(),
        name="auth-verify-reset-otp",
    ),
    path("auth/reset-password/", views.ResetPasswordView.as_view(), name="auth-reset-password"),
    # Profile
    path("users/profile/", views.ProfileView.as_view(), name="users-profile"),
    path(
        "users/change-password/", views.ChangePasswordView.as_view(), name="users-change-password"
    ),
    # Account Deletion
    path("auth/account/", views.DeleteAccountView.as_view(), name="auth-delete-account"),
]
