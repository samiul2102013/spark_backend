from django.urls import path

from . import views

urlpatterns = [
    path("bookings/", views.BookingListView.as_view(), name="booking-list"),
    path("bookings/<int:booking_id>/", views.BookingDetailView.as_view(), name="booking-detail"),
    path("bookings/<int:booking_id>/cancel/", views.BookingCancelView.as_view(), name="booking-cancel"),
    path("bookings/slots/", views.HubSlotsView.as_view(), name="booking-slots"),
]
