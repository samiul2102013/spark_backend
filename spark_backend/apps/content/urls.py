from django.urls import path

from . import views

urlpatterns = [
    # Mobile / Public
    path("content/privacy-policy/", views.PrivacyPolicyView.as_view(), name="privacy-policy"),
    path("content/terms/", views.TermsView.as_view(), name="terms-and-conditions"),
    # Admin
    path("admin/content/privacy-policy/", views.AdminPrivacyPolicyView.as_view(), name="admin-privacy-policy"),
    path("admin/content/terms/", views.AdminTermsView.as_view(), name="admin-terms"),
]
