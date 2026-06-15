from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.hubs.models import Hub
from core.exceptions import BookingConflictError

from .models import Booking


class BookingService:
    def list_bookings(self, user=None, hub_id=None, status=None, date=None):
        qs = Booking.objects.select_related("user", "hub").all()
        if user:
            qs = qs.filter(user=user)
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        if status:
            qs = qs.filter(status=status)
        if date:
            qs = qs.filter(start_time__date=date)
        return qs.order_by("-start_time")

    def get_booking(self, booking_id):
        return Booking.objects.select_related("user", "hub").get(id=booking_id)

    @transaction.atomic
    def create_booking(self, user, data):
        hub_id = data.pop("hub")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        hub = Hub.objects.get(id=hub_id)
        concurrent = Booking.objects.filter(
            hub=hub, status="active", start_time__lt=end_time, end_time__gt=start_time
        ).count()
        if concurrent >= hub.max_concurrent_bookings:
            raise BookingConflictError("Hub is at full capacity for this time slot.")
        return Booking.objects.create(user=user, hub=hub, **data)

    @transaction.atomic
    def cancel_booking(self, booking_id, user):
        booking = self.get_booking(booking_id)
        booking.status = "cancelled"
        booking.save(update_fields=["status"])
        return booking

    @transaction.atomic
    def complete_booking(self, booking_id):
        booking = self.get_booking(booking_id)
        booking.status = "completed"
        booking.save(update_fields=["status"])
        return booking

    def get_available_slots(self, hub_id, date):
        hub = Hub.objects.get(id=hub_id)
        bookings = Booking.objects.filter(
            hub_id=hub_id, status="active", start_time__date=date
        )
        slots = []
        start = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.min.time()))
        for hour in range(6, 22):
            slot_start = start + timedelta(hours=hour)
            slot_end = slot_start + timedelta(hours=1)
            concurrent = bookings.filter(
                start_time__lt=slot_end, end_time__gt=slot_start
            ).count()
            slots.append({
                "start_time": slot_start.isoformat(),
                "available": concurrent < hub.max_concurrent_bookings,
            })
        return slots
