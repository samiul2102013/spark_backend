from django.urls import path

from . import views

urlpatterns = [
    path("content/privacy-policy/", views.PrivacyPolicyView.as_view(), name="privacy-policy"),
    path("content/terms/", views.TermsView.as_view(), name="terms-and-conditions"),
]
