from django.db import transaction

from core.exceptions import BookingConflictError

from .models import Booking


class BookingService:
    @staticmethod
    def list_bookings(user=None, hub_id=None, status=None):
        qs = Booking.objects.select_related("user", "hub").all()
        if user:
            qs = qs.filter(user=user)
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        if status:
            qs = qs.filter(status=status)
        return qs

    @staticmethod
    def get_booking(booking_id):
        return Booking.objects.select_related("user", "hub").get(id=booking_id)

    @staticmethod
    @transaction.atomic
    def create_booking(user, hub, start_time, end_time, client_uuid=None):
        concurrent = Booking.objects.filter(
            hub=hub, status="active", start_time__lt=end_time, end_time__gt=start_time
        ).count()
        if concurrent >= hub.max_concurrent_bookings:
            raise BookingConflictError("Hub is at full capacity for this time slot.")
        return Booking.objects.create(
            user=user, hub=hub, start_time=start_time, end_time=end_time, client_uuid=client_uuid
        )

    @staticmethod
    @transaction.atomic
    def cancel_booking(booking_id):
        booking = Booking.objects.get(id=booking_id)
        booking.status = "cancelled"
        booking.save()
        return booking

    @staticmethod
    @transaction.atomic
    def complete_booking(booking_id):
        booking = Booking.objects.get(id=booking_id)
        booking.status = "completed"
        booking.save()
        return booking
