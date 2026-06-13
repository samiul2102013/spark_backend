from django.urls import path

from . import views

urlpatterns = [
    path("bookings/", views.booking_list_view, name="booking-list"),
    path("bookings/<int:booking_id>/", views.booking_detail_view, name="booking-detail"),
    path("bookings/create/", views.booking_create_view, name="booking-create"),
    path("bookings/<int:booking_id>/cancel/", views.booking_cancel_view, name="booking-cancel"),
    path(
        "bookings/<int:booking_id>/complete/", views.booking_complete_view, name="booking-complete"
    ),
]
