from django.db import transaction

from core.exceptions import BookingConflictError

from .models import Booking


class BookingService:
    @staticmethod
    @transaction.atomic()
    def create_booking(user, hub, start_time, end_time):
        concurrent = Booking.objects.filter(
            hub=hub, status="active", start_time__lt=end_time, end_time__gt=start_time
        ).count()
        if concurrent >= hub.max_concurrent_bookings:
            raise BookingConflictError("Hub is at full capacity for this time slot.")
        return Booking.objects.create(user=user, hub=hub, start_time=start_time, end_time=end_time)
