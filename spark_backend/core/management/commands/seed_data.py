from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone


def _get_or_create_user(User, phone, full_name, role, hub=None, lat=None, lng=None):
    defaults = {
        "full_name": full_name,
        "role": role,
        "is_active": True,
        "is_invite_accepted": True,
    }
    if hub:
        defaults["hub"] = hub
    if lat is not None:
        defaults["latitude"] = lat
    if lng is not None:
        defaults["longitude"] = lng
    u, _ = User.objects.get_or_create(phone_number=phone, defaults=defaults)
    return u


class Command(BaseCommand):
    help = "Seed the database with realistic Jamaican hurricane / cyclone scenario data"

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model
        from apps.bookings.models import Booking
        from apps.comms.models import Broadcast, CheckIn, Notification
        from apps.hazards.models import Comment, Hazard
        from apps.hubs.models import Hub

        User = get_user_model()
        now = timezone.now()

        # ── Hubs ──────────────────────────────────────────────────────
        hubs_data = [
            ("Kingston Emergency Hub", "23 King Street, Kingston", 17.9712, -76.7936,
             "open", 92, 1200, 850, 48.5, True, 15),
            ("Montego Bay Shelter", "42 Harbour Street, Montego Bay", 18.4704, -77.9183,
             "open", 78, 900, 600, 36.2, True, 10),
            ("Ocho Rios Community Hub", "15 Main Street, Ocho Rios", 18.4088, -77.1021,
             "open", 65, 750, 500, 28.0, True, 8),
            ("Port Antonio Relief Center", "8 West Street, Port Antonio", 18.1757, -76.4503,
             "open", 55, 600, 400, 22.5, True, 6),
            ("Mandeville Operations Hub", "3 Perth Road, Mandeville", 18.0350, -77.5035,
             "low_battery", 18, 200, 150, 6.0, True, 5),
            ("Negril Disaster Hub", "7 Norman Manley Blvd, Negril", 18.2705, -78.3482,
             "open", 88, 1100, 780, 40.0, True, 12),
            ("Spanish Town Response Hub", "12 Burke Road, Spanish Town", 17.9928, -76.9580,
             "open", 72, 850, 620, 34.5, True, 8),
            ("Savanna-la-Mar Hub", "5 Great George Street, Savanna-la-Mar", 18.2203, -78.1348,
             "critical", 8, 180, 90, 2.5, False, 4),
            ("St. Ann's Bay Hub", "22 Evelyn Avenue, St. Ann's Bay", 18.4362, -77.1996,
             "open", 60, 700, 480, 26.0, True, 6),
            ("Falmouth Emergency Center", "10 Market Street, Falmouth", 18.4930, -77.6561,
             "low_battery", 22, 300, 210, 8.0, True, 5),
        ]

        coord = _get_or_create_user(User, "01856669500", "Andrew Shirley", "coordinator")

        for name, addr, lat, lng, status, batt, sol_in, sol_out, runtime, starlink, max_books in hubs_data:
            Hub.objects.get_or_create(
                name=name,
                defaults={
                    "address": addr,
                    "latitude": lat,
                    "longitude": lng,
                    "status": status,
                    "battery_percentage": batt,
                    "solar_input_w": sol_in,
                    "solar_output_w": sol_out,
                    "estimated_runtime_h": runtime,
                    "starlink_status": starlink,
                    "max_concurrent_bookings": max_books,
                    "coordinator": coord,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Created {len(hubs_data)} hubs"))

        kingston_hub = Hub.objects.get(name="Kingston Emergency Hub")
        mobay_hub = Hub.objects.get(name="Montego Bay Shelter")

        # ── Residents ────────────────────────────────────────────────
        residents = [
            ("01856669501", "Winston Brown", kingston_hub, 17.9715, -76.7890),
            ("01856669502", "Marcia Campbell", kingston_hub, 17.9730, -76.7910),
            ("01856669503", "Donovan Reid", kingston_hub, 17.9680, -76.7950),
            ("01856669504", "Pauline Mitchell", mobay_hub, 18.4710, -77.9190),
            ("01856669505", "Derrick Thompson", mobay_hub, 18.4690, -77.9160),
            ("01856669506", "Carmen Williams", kingston_hub, 17.9700, -76.7900),
            ("01856669507", "Lloyd Clarke", kingston_hub, 17.9740, -76.7880),
            ("01856669508", "Patricia Johnson", mobay_hub, 18.4720, -77.9200),
            ("01856669509", "Michael Barnes", kingston_hub, 17.9690, -76.7940),
            ("01856669510", "Sandra Morrison", mobay_hub, 18.4680, -77.9170),
        ]
        residents_created = 0
        users_created = []
        for phone, name, hub, lat, lng in residents:
            u = _get_or_create_user(User, phone, name, "resident", hub=hub, lat=lat, lng=lng)
            users_created.append(u)
            residents_created += 1
        self.stdout.write(self.style.SUCCESS(f"Created / activated {residents_created} residents"))

        # ── Hazards (Cyclone Scenario) ───────────────────────────────
        hazards_data = [
            ("flooding", "Severe flooding on King Street, Kingston. Water levels rising rapidly after continuous rainfall from Tropical Storm.", kingston_hub, 17.9712, -76.7936, 3, "active", "post"),
            ("fallen_tree", "Large tree fallen across Mandela Highway near the UWI roundabout. Road impassable.", kingston_hub, 17.9830, -76.7840, 2, "active", "post"),
            ("power_line_down", "Power line down on Washington Boulevard, Portmore. Live wires on road. Keep distance.", kingston_hub, 17.9700, -76.8820, 3, "active", "post"),
            ("blocked_road", "Landslide blocking Junction Main Road, St. Elizabeth. No alternative route currently.", mobay_hub, 18.1200, -77.4500, 2, "active", "post"),
            ("landslide", "Hillside collapsed on Junction Main Road, St. Mary. Extensive debris clean-up needed.", mobay_hub, 18.2200, -76.9000, 2, "active", "post"),
            ("collapsed_building", "Partial building collapse on Spanish Town Road, Trench Town. Rescue teams dispatched.", kingston_hub, 17.9870, -76.8020, 3, "active", "post"),
            ("flooding", "Flooding on Barnett Street, Montego Bay. Businesses and homes affected. Sandbags available at hub.", mobay_hub, 18.4710, -77.9220, 2, "active", "post"),
            ("fallen_tree", "Fallen tree blocking A1 Highway near Green Island, Negril. Single lane passable.", mobay_hub, 18.3900, -78.2700, 1, "active", "post"),
            ("power_line_down", "Downed power lines on Main Street, Ocho Rios. JPS crew en route.", mobay_hub, 18.4100, -77.1040, 2, "active", "post"),
            ("blocked_road", "Road blocked by debris in Buff Bay, Portland. Clearing underway by NWA.", kingston_hub, 18.2280, -76.6610, 1, "active", "post"),
            ("flooding", "Flash flooding along the Rio Cobre near Spanish Town. Residents advised to move to higher ground.", kingston_hub, 17.9920, -76.9590, 3, "active", "post"),
            ("medical", "Elderly resident in Tivoli Gardens requires urgent medical evacuation. Road access limited.", kingston_hub, 17.9780, -76.8050, 3, "active", "post"),
        ]

        for cat, desc, hub, lat, lng, sev, status, period in hazards_data:
            Hazard.objects.get_or_create(
                description=desc[:255],
                defaults={
                    "category": cat,
                    "latitude": lat,
                    "longitude": lng,
                    "severity": sev,
                    "status": status,
                    "period": period,
                    "hub": hub,
                    "reporter": coord,
                    "source": "app",
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Created {len(hazards_data)} hazards"))

        # ── Comments on hazards ──────────────────────────────────────
        hazard = Hazard.objects.filter(status="active").first()
        if hazard:
            comments_data = [
                ("Crew dispatched to assess flooding on King Street. ETA 15 minutes.", coord),
                ("Water level has risen by 2 feet in the last hour. Residents being evacuated.", users_created[0] if users_created else coord),
                ("ODPEM monitoring the situation. Additional sandbags on the way.", coord),
                ("Road closed to all traffic. Use alternative route via Mountain View Avenue.", users_created[1] if len(users_created) > 1 else coord),
            ]
            for body, author in comments_data:
                Comment.objects.get_or_create(
                    hazard=hazard,
                    author=author,
                    body=body,
                )
            self.stdout.write(self.style.SUCCESS(f"Created {len(comments_data)} comments on hazard #{hazard.id}"))

        # ── Check-ins ────────────────────────────────────────────────
        checkin_statuses = ["safe", "need_assistance"]
        checkin_count = 0
        for i, u in enumerate(users_created[:6]):
            hub = kingston_hub if i < 4 else mobay_hub
            CheckIn.objects.get_or_create(
                user=u,
                hub=hub,
                timestamp=now - timedelta(hours=4, minutes=i * 30),
                defaults={
                    "people_count": 2 + (i % 3),
                    "status": checkin_statuses[i % 2],
                    "road_access": "blocked" if i % 3 == 0 else "open",
                    "medical_notes": "" if i % 2 == 0 else "Needs asthma medication",
                    "latitude": u.latitude,
                    "longitude": u.longitude,
                    "channel": "app",
                },
            )
            checkin_count += 1
        self.stdout.write(self.style.SUCCESS(f"Created {checkin_count} check-ins"))

        # ── Bookings ─────────────────────────────────────────────────
        booking_start = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        for i, u in enumerate(users_created[:4]):
            hub = kingston_hub if i < 2 else mobay_hub
            start = booking_start + timedelta(hours=i * 3)
            end = start + timedelta(hours=2)
            Booking.objects.get_or_create(
                user=u,
                hub=hub,
                start_time=start,
                defaults={
                    "end_time": end,
                    "status": "active",
                    "people_count": 1 + (i % 3),
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Created 4 bookings"))

        # ── Broadcasts ───────────────────────────────────────────────
        broadcasts_data = [
            (kingston_hub, "Tropical Storm Warning", "A tropical storm warning is in effect for Jamaica. Residents in low-lying areas should prepare for possible flooding and evacuate if necessary. Emergency shelters are open.", "urgent"),
            (kingston_hub, "Curfew in Effect", "A curfew is in effect from 6 PM to 6 AM in Kingston and St. Andrew. Essential workers exempted with proper ID.", "warning"),
            (mobay_hub, "Road Closures Update", "Mandela Highway and Washington Boulevard are closed due to flooding. Use Mannings Hill Road as alternative route.", "warning"),
            (kingston_hub, "Emergency Contact Numbers", "ODPEM: 119, JPS Power Outages: 118, Police Emergency: 119, Fire Department: 110. Share with your neighbours.", "info"),
            (mobay_hub, "Water Distribution Points", "Water distribution points open at Montego Bay Hub and Sam Sharpe Square. Bring containers. 10 AM - 4 PM.", "info"),
        ]
        for hub, subject, body, priority in broadcasts_data:
            Broadcast.objects.get_or_create(
                hub=hub,
                subject=subject,
                defaults={
                    "body": body,
                    "priority": priority,
                    "sender": coord,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Created {len(broadcasts_data)} broadcasts"))

        # ── Notifications ────────────────────────────────────────────
        for u in users_created[:6]:
            Notification.objects.get_or_create(
                user=u,
                title="Tropical Storm Warning",
                defaults={
                    "type": "alert",
                    "body": "A tropical storm warning is in effect. Stay indoors and monitor local news.",
                    "read": False,
                    "hub": u.hub,
                },
            )
            Notification.objects.get_or_create(
                user=u,
                title="Hub Status Update",
                defaults={
                    "type": "hub_status",
                    "body": f"{u.hub.name} is open. Charge your devices and check in to confirm your safety.",
                    "read": False,
                    "hub": u.hub,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Created notifications for residents"))

        self.stdout.write(self.style.SUCCESS("\n✓ Jamaican cyclone scenario data seeded successfully"))
