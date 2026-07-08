from django.urls import path

from . import views

urlpatterns = [
    # Mobile / Public
    path("content/privacy-policy/", views.PrivacyPolicyView.as_view(), name="privacy-policy"),
    path("content/terms/", views.TermsView.as_view(), name="terms-and-conditions"),
    path("content/account-deletion-policy/", views.AccountDeletionPolicyView.as_view(), name="account-deletion-policy"),
    # Admin
    path("admin/content/privacy-policy/", views.AdminPrivacyPolicyView.as_view(), name="admin-privacy-policy"),
    path("admin/content/terms/", views.AdminTermsView.as_view(), name="admin-terms"),
    path("admin/content/account-deletion-policy/", views.AdminAccountDeletionPolicyView.as_view(), name="admin-account-deletion-policy"),
]
