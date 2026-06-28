from rest_framework import serializers

from apps.bookings.models import Booking
from apps.comms.models import CheckIn, InboundMessage
from apps.hazards.models import Hazard
from apps.hubs.models import Hub
from apps.users.models import User


class AdminProfileSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="phone_number", read_only=True)

    class Meta:
        model = User
        fields = ["id", "phone_number", "full_name", "email", "role"]
        read_only_fields = ["id", "role"]


class AdminUserListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="phone_number", read_only=True)
    hub_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "phone_number", "full_name", "email", "role",
            "is_active", "hub_name", "created_at",
        ]

    def get_hub_name(self, obj):
        return obj.hub.name if obj.hub else None


class ResidentListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="phone_number", read_only=True)
    hub_name = serializers.SerializerMethodField()
    community = serializers.SerializerMethodField()
    last_checkin = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "phone_number", "full_name", "email", "role",
            "is_active", "hub_name", "community", "last_checkin",
            "profile_photo", "household_size", "created_at",
        ]

    def get_hub_name(self, obj):
        return obj.hub.name if obj.hub else None

    def get_community(self, obj):
        return obj.hub.address if obj.hub else None

    def get_last_checkin(self, obj):
        checkin = CheckIn.objects.filter(user=obj).order_by("-timestamp").first()
        return checkin.timestamp.isoformat() if checkin else None

    def get_profile_photo(self, obj):
        request = self.context.get("request")
        if request and obj.profile_photo:
            return request.build_absolute_uri(obj.profile_photo.url)
        return None


class ResidentDetailSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="phone_number", read_only=True)
    hub_name = serializers.SerializerMethodField()
    community = serializers.SerializerMethodField()
    last_checkin = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()
    checkins_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "phone_number", "full_name", "email", "role",
            "household_size", "medical_needs", "is_active",
            "hub_name", "community", "latitude", "longitude",
            "last_checkin", "profile_photo", "checkins_count",
            "created_at",
        ]

    def get_hub_name(self, obj):
        return obj.hub.name if obj.hub else None

    def get_community(self, obj):
        return obj.hub.address if obj.hub else None

    def get_last_checkin(self, obj):
        checkin = CheckIn.objects.filter(user=obj).order_by("-timestamp").first()
        return checkin.timestamp.isoformat() if checkin else None

    def get_profile_photo(self, obj):
        request = self.context.get("request")
        if request and obj.profile_photo:
            return request.build_absolute_uri(obj.profile_photo.url)
        return None

    def get_checkins_count(self, obj):
        return CheckIn.objects.filter(user=obj).count()


class CoordinatorListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="phone_number", read_only=True)
    hub_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "phone_number", "full_name", "email",
            "is_active", "hub_name", "created_at",
        ]

    def get_hub_name(self, obj):
        return obj.hub.name if obj.hub else None


class CoordinatorDetailSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="phone_number", read_only=True)
    hub = serializers.SerializerMethodField()
    checkins_managed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "phone_number", "full_name", "email", "role",
            "is_active", "hub", "checkins_managed", "created_at",
        ]

    def get_hub(self, obj):
        if obj.hub:
            return {
                "id": obj.hub.id,
                "name": obj.hub.name,
                "address": obj.hub.address,
            }
        return None

    def get_checkins_managed(self, obj):
        if obj.hub:
            return CheckIn.objects.filter(hub=obj.hub).count()
        return 0


class AdminHubListSerializer(serializers.ModelSerializer):
    coordinator_name = serializers.SerializerMethodField()
    residents_count = serializers.SerializerMethodField()

    class Meta:
        model = Hub
        fields = [
            "id", "name", "address", "status", "battery_percentage",
            "starlink_status", "coordinator_name", "residents_count",
        ]

    def get_coordinator_name(self, obj):
        return obj.coordinator.full_name if obj.coordinator else None

    def get_residents_count(self, obj):
        return User.objects.filter(hub=obj).count()


class AdminHubDetailSerializer(serializers.ModelSerializer):
    coordinator = serializers.SerializerMethodField()
    residents_count = serializers.SerializerMethodField()
    active_bookings = serializers.SerializerMethodField()
    last_resident_checkin = serializers.SerializerMethodField()
    recent_checkins = serializers.SerializerMethodField()
    recent_hazards = serializers.SerializerMethodField()

    class Meta:
        model = Hub
        fields = "__all__"

    def get_coordinator(self, obj):
        if obj.coordinator:
            return {
                "phone_number": obj.coordinator.phone_number,
                "full_name": obj.coordinator.full_name,
                "is_active": obj.coordinator.is_active,
            }
        return None

    def get_residents_count(self, obj):
        return User.objects.filter(hub=obj).count()

    def get_active_bookings(self, obj):
        return Booking.objects.filter(hub=obj, status="active").count()

    def get_last_resident_checkin(self, obj):
        checkin = CheckIn.objects.filter(hub=obj).order_by("-timestamp").first()
        return checkin.timestamp.isoformat() if checkin else None

    def get_recent_checkins(self, obj):
        qs = CheckIn.objects.filter(hub=obj).order_by("-timestamp")[:10]
        return [
            {
                "id": c.id,
                "user_name": c.user.full_name,
                "status": c.status,
                "timestamp": c.timestamp.isoformat(),
            }
            for c in qs
        ]

    def get_recent_hazards(self, obj):
        qs = Hazard.objects.filter(hub=obj).order_by("-created_at")[:10]
        return [
            {
                "id": h.id,
                "category": h.category,
                "severity": h.severity,
                "status": h.status,
                "created_at": h.created_at.isoformat(),
            }
            for h in qs
        ]


class HubCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    address = serializers.CharField(required=False, allow_blank=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    max_concurrent_bookings = serializers.IntegerField(default=5)
    coordinator_id = serializers.CharField(required=False, allow_null=True)


class AssignCoordinatorSerializer(serializers.Serializer):
    coordinator_id = serializers.CharField()


class ReassignCoordinatorSerializer(serializers.Serializer):
    new_coordinator_id = serializers.CharField()


class InviteUserSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    full_name = serializers.CharField()
    role = serializers.ChoiceField(choices=["resident", "coordinator", "government"])
    hub_id = serializers.IntegerField(required=False, allow_null=True)


class RoleDetailSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="phone_number", read_only=True)

    class Meta:
        model = User
        fields = ["id", "phone_number", "full_name", "role", "is_active", "is_staff", "created_at"]


class SuspendUserSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class AdminOverviewSerializer(serializers.Serializer):
    checkins = serializers.DictField()
    active_hubs = serializers.IntegerField()
    hazard_reports = serializers.IntegerField()
    silent_communications = serializers.IntegerField()
    urgent_flags = serializers.DictField()
    checkins_over_time = serializers.ListField()
    hazard_breakdown = serializers.DictField()
    users = serializers.DictField()
    messages = serializers.DictField()


class UserStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    residents = serializers.IntegerField()
    coordinators = serializers.IntegerField()
    active = serializers.IntegerField()


class MessageStatsSerializer(serializers.Serializer):
    inbound_today = serializers.IntegerField()
    unclassified = serializers.IntegerField()
