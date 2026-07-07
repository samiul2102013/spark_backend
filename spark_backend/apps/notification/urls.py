from django.urls import path

from . import views

urlpatterns = [
    path("devices/register/", views.DeviceRegisterView.as_view(), name="device-register"),
    path("devices/unregister/", views.DeviceUnregisterView.as_view(), name="device-unregister"),
]
