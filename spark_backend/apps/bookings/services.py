from datetime import timedelta

from django.db import transaction
from django.db.models import Sum
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
        device_count = data.get("device_count", 1)
        start_time = data.pop("start_time")
        end_time = data.pop("end_time", None)
        if not end_time:
            end_time = start_time + timedelta(minutes=30)
        hub = Hub.objects.get(id=hub_id)
        concurrent = Booking.objects.filter(
            hub=hub, status="active", start_time__lt=end_time, end_time__gt=start_time
        ).count()
        if concurrent >= hub.max_concurrent_bookings:
            raise BookingConflictError("Hub is at full capacity for this time slot.")
        used_ports = Booking.objects.filter(hub=hub, status="active").aggregate(
            total=Sum("device_count")
        )["total"] or 0
        if used_ports + device_count > hub.total_ports:
            raise BookingConflictError(
                f"Not enough available ports. {hub.total_ports - used_ports} port(s) remaining."
            )
        return Booking.objects.create(user=user, hub=hub, start_time=start_time, end_time=end_time, **data)

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

    def _auto_complete_expired(self):
        now = timezone.now()
        Booking.objects.filter(status="active", end_time__lte=now).update(status="completed")

    def get_available_slots(self, hub_id, date, user=None):
        self._auto_complete_expired()
        hub = Hub.objects.get(id=hub_id)
        bookings = Booking.objects.filter(hub_id=hub_id, status="active", start_time__date=date)
        slots = []
        start = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.min.time()))
        for hour in range(6, 22):
            for minute in (0, 30):
                slot_start = start + timedelta(hours=hour, minutes=minute)
                slot_end = slot_start + timedelta(minutes=30)
                concurrent = bookings.filter(start_time__lt=slot_end, end_time__gt=slot_start).count()
                is_available = concurrent < hub.max_concurrent_bookings
                is_booked_by_user = False
                if user:
                    is_booked_by_user = bookings.filter(
                        user=user, start_time__lt=slot_end, end_time__gt=slot_start
                    ).exists() if not is_available else False
                slots.append(
                    {
                        "start_time": slot_start.isoformat(),
                        "end_time": slot_end.isoformat(),
                        "available": is_available,
                        "booked": is_booked_by_user,
                        "battery_percentage": hub.battery_percentage,
                    }
                )
        return slots

    def get_hub_slots(self, hub_id, date, user=None):
        return self.get_available_slots(hub_id, date, user)
