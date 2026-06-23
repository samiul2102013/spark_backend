from django.db.models import Q
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.ai.models import AIConfig, SituationReport
from apps.bookings.models import Booking
from apps.comms.models import CheckIn, InboundMessage
from apps.hazards.models import Hazard
from apps.hubs.models import Hub
from apps.users.models import User
from apps.users.permissions import IsAdmin
from apps.users.serializers import InviteGovernmentSerializer, ProfileSerializer
from apps.users.services import AuthService
from core.pagination import StandardPagination
from core.responses import created_response, error_response, success_response

HUB_STATUSES = ["open", "closed", "low_battery", "critical"]
MESSAGE_STATUSES = ["pending", "classified", "unclassified"]
MESSAGE_SOURCES = ["whatsapp", "sms"]

# ─── Serializers ─────────────────────────────────────────────────────


class ResidentListSerializer(serializers.ModelSerializer):
    hub_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "phone_number",
            "full_name",
            "email",
            "role",
            "is_active",
            "hub_name",
            "household_size",
            "created_at",
        ]

    def get_hub_name(self, obj):
        return obj.hub.name if obj.hub else None


class ResidentDetailSerializer(serializers.ModelSerializer):
    hub_name = serializers.SerializerMethodField()
    checkins_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "phone_number",
            "full_name",
            "email",
            "role",
            "household_size",
            "medical_needs",
            "is_active",
            "hub_name",
            "latitude",
            "longitude",
            "checkins_count",
            "created_at",
        ]

    def get_hub_name(self, obj):
        return obj.hub.name if obj.hub else None

    def get_checkins_count(self, obj):
        return CheckIn.objects.filter(user=obj).count()


class CoordinatorListSerializer(serializers.ModelSerializer):
    hub_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["phone_number", "full_name", "email", "is_active", "hub_name", "created_at"]

    def get_hub_name(self, obj):
        return obj.hub.name if obj.hub else None


class CoordinatorDetailSerializer(serializers.ModelSerializer):
    hub = serializers.SerializerMethodField()
    checkins_managed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "phone_number",
            "full_name",
            "email",
            "role",
            "is_active",
            "hub",
            "checkins_managed",
            "created_at",
        ]

    def get_hub(self, obj):
        if obj.hub:
            from apps.hubs.serializers import HubSerializer

            return HubSerializer(obj.hub).data
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
            "id",
            "name",
            "address",
            "status",
            "battery_percentage",
            "starlink_status",
            "coordinator_name",
            "residents_count",
        ]

    def get_coordinator_name(self, obj):
        return obj.coordinator.full_name if obj.coordinator else None

    def get_residents_count(self, obj):
        return User.objects.filter(hub=obj).count()


class AdminHubDetailSerializer(serializers.ModelSerializer):
    coordinator = serializers.SerializerMethodField()
    residents_count = serializers.SerializerMethodField()
    active_bookings = serializers.SerializerMethodField()
    recent_checkins = serializers.SerializerMethodField()
    recent_hazards = serializers.SerializerMethodField()

    class Meta:
        model = Hub
        fields = "__all__"

    def get_coordinator(self, obj):
        if obj.coordinator:
            return CoordinatorListSerializer(obj.coordinator).data
        return None

    def get_residents_count(self, obj):
        return User.objects.filter(hub=obj).count()

    def get_active_bookings(self, obj):
        return Booking.objects.filter(hub=obj, status="active").count()

    def get_recent_checkins(self, obj):
        from apps.comms.serializers import CheckInSerializer

        qs = CheckIn.objects.filter(hub=obj).order_by("-timestamp")[:10]
        return CheckInSerializer(qs, many=True).data

    def get_recent_hazards(self, obj):
        from apps.hazards.serializers import HazardSerializer

        qs = Hazard.objects.filter(hub=obj).order_by("-created_at")[:10]
        return HazardSerializer(qs, many=True).data


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


class RoleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["phone_number", "full_name", "role", "is_active", "is_staff", "created_at"]


class SuspendUserSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class InviteUserSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    full_name = serializers.CharField()
    role = serializers.ChoiceField(choices=["resident", "coordinator", "government"])
    hub_id = serializers.IntegerField(required=False, allow_null=True)


class InboundMessageAdminSerializer(serializers.ModelSerializer):
    classified_hazard_category = serializers.SerializerMethodField()

    class Meta:
        model = InboundMessage
        fields = "__all__"

    def get_classified_hazard_category(self, obj):
        return obj.classified_hazard.category if obj.classified_hazard else None


class AIConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIConfig
        exclude = ["api_key_encrypted"]


class UserStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    residents = serializers.IntegerField()
    coordinators = serializers.IntegerField()
    active = serializers.IntegerField()


class MessageStatsSerializer(serializers.Serializer):
    inbound_today = serializers.IntegerField()
    unclassified = serializers.IntegerField()


class AdminOverviewSerializer(serializers.Serializer):
    hubs = serializers.DictField()
    hazards = serializers.DictField()
    bookings = serializers.DictField()
    checkins = serializers.DictField()
    users = UserStatsSerializer()
    messages = MessageStatsSerializer()


# ─── Services ────────────────────────────────────────────────────────


class AdminUserService:
    def list_residents(self, hub_id=None, is_active=None, search=None):
        qs = User.objects.filter(role="resident")
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search)
                | Q(phone_number__icontains=search)
                | Q(email__icontains=search)
            )
        return qs

    def get_resident(self, user_id):
        return User.objects.get(id=user_id, role="resident")

    def list_coordinators(self, hub_id=None, is_active=None, search=None):
        qs = User.objects.filter(role="coordinator")
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search)
                | Q(phone_number__icontains=search)
                | Q(email__icontains=search)
            )
        return qs

    def get_coordinator(self, user_id):
        return User.objects.get(id=user_id, role="coordinator")

    def suspend_user(self, user_id):
        user = User.objects.get(id=user_id)
        user.is_active = False
        user.save(update_fields=["is_active"])
        return user

    def activate_user(self, user_id):
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save(update_fields=["is_active"])
        return user

    def invite_user(self, data):
        phone = data.get("phone_number")
        user = User.objects.filter(phone_number=phone).first()
        if user:
            user.full_name = data.get("full_name", user.full_name)
            user.role = data.get("role", user.role)
            user.hub_id = data.get("hub_id", user.hub_id)
            user.is_active = True
            user.save()
            return user

        user = User.objects.create_user(
            phone_number=phone,
            full_name=data["full_name"],
            role=data["role"],
            hub_id=data.get("hub_id"),
            is_active=True,
        )
        return user

    def set_role(self, user_id, role):
        user = User.objects.get(id=user_id)
        if role not in ("resident", "coordinator", "government", "admin"):
            raise ValueError("Invalid role.")
        user.role = role
        user.save(update_fields=["role"])
        return user


class AdminHubService:
    def list_hubs(self, status=None, search=None):
        qs = Hub.objects.select_related("coordinator").all()
        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(address__icontains=search))
        return qs

    def get_hub(self, hub_id):
        return Hub.objects.select_related("coordinator").get(id=hub_id)

    def create_hub(self, data):
        coordinator_id = data.pop("coordinator_id", None)
        hub = Hub.objects.create(**data)
        if coordinator_id:
            try:
                coord = User.objects.get(phone_number=coordinator_id, role="coordinator")
                hub.coordinator = coord
                hub.save(update_fields=["coordinator"])
            except User.DoesNotExist:
                pass
        return hub

    def assign_coordinator(self, hub_id, coordinator_id):
        hub = Hub.objects.get(id=hub_id)
        coord = User.objects.get(phone_number=coordinator_id)
        hub.coordinator = coord
        hub.save(update_fields=["coordinator"])
        return hub

    def reassign_coordinator(self, hub_id, new_coordinator_id):
        hub = Hub.objects.get(id=hub_id)
        coord = User.objects.get(phone_number=new_coordinator_id)
        hub.coordinator = coord
        hub.save(update_fields=["coordinator"])
        return hub


class AdminReportService:
    def list_reports(self, hub_id=None, is_auto=None):
        qs = SituationReport.objects.select_related("hub").all()
        if hub_id:
            qs = qs.filter(hub_id=hub_id)
        if is_auto is not None:
            qs = qs.filter(is_auto=is_auto)
        return qs.order_by("-created_at")

    def get_report(self, report_id):
        return SituationReport.objects.select_related("hub").get(id=report_id)

    def get_ai_config(self):
        return AIConfig.objects.first()

    def update_ai_config(self, data):
        config = AIConfig.objects.first()
        if not config:
            config = AIConfig.objects.create()
        for key, value in data.items():
            setattr(config, key, value)
        config.save()
        return config


class AdminMessageService:
    def list_messages(self, status=None, source=None, search=None):
        qs = InboundMessage.objects.select_related("classified_hazard").all()
        if status:
            qs = qs.filter(status=status)
        if source:
            qs = qs.filter(source=source)
        if search:
            qs = qs.filter(Q(from_number__icontains=search) | Q(body__icontains=search))
        return qs

    def get_message(self, message_id):
        return InboundMessage.objects.select_related("classified_hazard").get(id=message_id)

    def classify_message(self, message_id, hazard_id):
        msg = InboundMessage.objects.get(id=message_id)
        hazard = Hazard.objects.get(id=hazard_id) if hazard_id else None
        msg.classified_hazard = hazard
        msg.status = "classified" if hazard else "unclassified"
        msg.save(update_fields=["classified_hazard", "status"])
        return msg


class AdminOverviewService:
    def overview(self):
        from django.utils import timezone

        today = timezone.now().date()
        users = User.objects.all()
        return {
            "hubs": {
                "total": Hub.objects.count(),
                "open": Hub.objects.filter(status="open").count(),
                "critical": Hub.objects.filter(status="critical").count(),
            },
            "hazards": {
                "active": Hazard.objects.filter(status="active").count(),
                "reported_today": Hazard.objects.filter(created_at__date=today).count(),
            },
            "bookings": {
                "active": Booking.objects.filter(status="active").count(),
                "today": Booking.objects.filter(start_time__date=today).count(),
            },
            "checkins": {
                "total_today": CheckIn.objects.filter(timestamp__date=today).count(),
                "safe": CheckIn.objects.filter(timestamp__date=today, status="safe").count(),
                "need_assistance": CheckIn.objects.filter(
                    timestamp__date=today, status="need_assistance"
                ).count(),
            },
            "users": {
                "total": users.count(),
                "residents": users.filter(role="resident").count(),
                "coordinators": users.filter(role="coordinator").count(),
                "active": users.filter(is_active=True).count(),
            },
            "messages": {
                "inbound_today": InboundMessage.objects.filter(created_at__date=today).count(),
                "unclassified": InboundMessage.objects.filter(status="unclassified").count(),
            },
        }


# ─── Views ───────────────────────────────────────────────────────────


class AdminOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Overview"],
        summary="Get admin overview",
        description="Retrieve aggregate platform statistics for the admin dashboard.",
        responses={200: AdminOverviewSerializer},
    )
    def get(self, request):
        try:
            service = AdminOverviewService()
            data = service.overview()
            return success_response(data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Users ────────────────────────────────────────────────────────────


class AdminResidentListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Residents"],
        summary="List residents",
        description="Retrieve paginated list of all resident users with optional filters.",
        parameters=[
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False, description="Filter by hub ID"),
            OpenApiParameter("is_active", bool, OpenApiParameter.QUERY, required=False, description="Filter by active status"),
            OpenApiParameter("search", str, OpenApiParameter.QUERY, required=False, description="Search by name, phone, or email"),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False, description="Page number"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="Results per page (max 100)"),
        ],
        responses={200: ResidentListSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = AdminUserService()
            qs = service.list_residents(
                hub_id=request.query_params.get("hub_id"),
                is_active=request.query_params.get("is_active"),
                search=request.query_params.get("search"),
            )
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = ResidentListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminResidentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Residents"],
        summary="Get resident details",
        description="Retrieve full details of a specific resident by user ID (phone number).",
        responses={200: ResidentDetailSerializer},
    )
    def get(self, request, user_id):
        try:
            service = AdminUserService()
            user = service.get_resident(user_id)
            serializer = ResidentDetailSerializer(user)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminResidentSuspendView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Residents"],
        summary="Suspend resident",
        description="Deactivate a resident account by ID.",
        responses={200: ResidentListSerializer},
    )
    def patch(self, request, user_id):
        try:
            service = AdminUserService()
            user = service.suspend_user(user_id)
            return success_response(ResidentListSerializer(user).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminResidentActivateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Residents"],
        summary="Activate resident",
        description="Reactivate a suspended resident account by ID.",
        responses={200: ResidentListSerializer},
    )
    def patch(self, request, user_id):
        try:
            service = AdminUserService()
            user = service.activate_user(user_id)
            return success_response(ResidentListSerializer(user).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminCoordinatorListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Coordinators"],
        summary="List coordinators",
        description="Retrieve paginated list of all coordinator users with optional filters.",
        parameters=[
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False, description="Filter by hub ID"),
            OpenApiParameter("is_active", bool, OpenApiParameter.QUERY, required=False, description="Filter by active status"),
            OpenApiParameter("search", str, OpenApiParameter.QUERY, required=False, description="Search by name, phone, or email"),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False, description="Page number"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="Results per page (max 100)"),
        ],
        responses={200: CoordinatorListSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = AdminUserService()
            qs = service.list_coordinators(
                hub_id=request.query_params.get("hub_id"),
                is_active=request.query_params.get("is_active"),
                search=request.query_params.get("search"),
            )
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = CoordinatorListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminCoordinatorDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Coordinators"],
        summary="Get coordinator details",
        description="Retrieve full details of a specific coordinator by user ID (phone number).",
        responses={200: CoordinatorDetailSerializer},
    )
    def get(self, request, user_id):
        try:
            service = AdminUserService()
            user = service.get_coordinator(user_id)
            serializer = CoordinatorDetailSerializer(user)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminCoordinatorSuspendView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Coordinators"],
        summary="Suspend coordinator",
        description="Deactivate a coordinator account by ID.",
        responses={200: CoordinatorListSerializer},
    )
    def patch(self, request, user_id):
        try:
            service = AdminUserService()
            user = service.suspend_user(user_id)
            return success_response(CoordinatorListSerializer(user).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminInviteUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Users"],
        summary="Invite user",
        description="Invite a new user (resident, coordinator, or government) by phone number.",
        request=InviteUserSerializer,
        responses={201: ProfileSerializer},
        examples=[
            OpenApiExample(
                "Invite User Example",
                value={
                    "phone_number": "01856669533",
                    "full_name": "John Doe",
                    "role": "resident",
                    "hub_id": 1,
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        try:
            serializer = InviteUserSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = AdminUserService()
            user = service.invite_user(serializer.validated_data)
            return created_response(ProfileSerializer(user).data)
        except ValueError as e:
            return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminInviteByEmailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "dashboard", "Users"],
        summary="Invite government user by email",
        description="Send an invitation email to a government user. Creates the user account and emails an invite link.",
        request=InviteGovernmentSerializer,
        responses={201: None},
        examples=[
            OpenApiExample(
                "Invite Government Example",
                value={
                    "email": "gov.official@example.com",
                    "full_name": "Jane Doe",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = InviteGovernmentSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            service = AuthService()
            result = service.invite_government(**serializer.validated_data)
            return created_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)


class AdminSetRoleView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Users"],
        summary="Set user role",
        description="Change a user's role (resident, coordinator, government, admin).",
        request=RoleDetailSerializer,
        responses={200: RoleDetailSerializer},
        examples=[
            OpenApiExample(
                "Set Role Example",
                value={"role": "coordinator"},
                request_only=True,
            ),
        ],
    )
    def patch(self, request, user_id):
        try:
            role = request.data.get("role")
            if not role:
                return error_response("Role is required.", http_status=status.HTTP_400_BAD_REQUEST)
            service = AdminUserService()
            user = service.set_role(user_id, role)
            return success_response(RoleDetailSerializer(user).data)
        except ValueError as e:
            return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Hubs ─────────────────────────────────────────────────────────────


class AdminHubListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Hubs"],
        summary="List hubs",
        description="Retrieve paginated list of all hubs for admin management.",
        parameters=[
            OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False, enum=HUB_STATUSES, description="Filter by hub status"),
            OpenApiParameter("search", str, OpenApiParameter.QUERY, required=False, description="Search by name or address"),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False, description="Page number"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="Results per page (max 100)"),
        ],
        responses={200: AdminHubListSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = AdminHubService()
            qs = service.list_hubs(
                status=request.query_params.get("status"),
                search=request.query_params.get("search"),
            )
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = AdminHubListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminHubDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Hubs"],
        summary="Get hub details",
        description="Retrieve full details of a specific hub for admin management.",
        responses={200: AdminHubDetailSerializer},
    )
    def get(self, request, hub_id):
        try:
            service = AdminHubService()
            hub = service.get_hub(hub_id)
            serializer = AdminHubDetailSerializer(hub)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminHubCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Hubs"],
        summary="Create hub",
        description="Create a new hub with location and capacity info.",
        request=HubCreateSerializer,
        responses={201: AdminHubListSerializer},
        examples=[
            OpenApiExample(
                "Create Hub Example",
                value={
                    "name": "Port Antonio Hub",
                    "address": "10 Harbour Street, Port Antonio",
                    "latitude": 18.1757,
                    "longitude": -76.4503,
                    "max_concurrent_bookings": 10,
                    "coordinator_id": "01856669533",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        try:
            serializer = HubCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = AdminHubService()
            hub = service.create_hub(serializer.validated_data)
            return created_response(AdminHubListSerializer(hub).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminHubAssignCoordinatorView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Hubs"],
        summary="Assign coordinator",
        description="Assign a coordinator to a hub by coordinator phone number.",
        request=AssignCoordinatorSerializer,
        responses={200: AdminHubListSerializer},
        examples=[
            OpenApiExample(
                "Assign Coordinator Example",
                value={"coordinator_id": "01856669533"},
                request_only=True,
            ),
        ],
    )
    def patch(self, request, hub_id):
        try:
            serializer = AssignCoordinatorSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = AdminHubService()
            hub = service.assign_coordinator(hub_id, serializer.validated_data["coordinator_id"])
            return success_response(AdminHubListSerializer(hub).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminHubReassignCoordinatorView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Hubs"],
        summary="Reassign coordinator",
        description="Replace the coordinator for a hub with a different coordinator by phone number.",
        request=ReassignCoordinatorSerializer,
        responses={200: AdminHubListSerializer},
        examples=[
            OpenApiExample(
                "Reassign Coordinator Example",
                value={"new_coordinator_id": "01856669534"},
                request_only=True,
            ),
        ],
    )
    def patch(self, request, hub_id):
        try:
            serializer = ReassignCoordinatorSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = AdminHubService()
            hub = service.reassign_coordinator(
                hub_id, serializer.validated_data["new_coordinator_id"]
            )
            return success_response(AdminHubListSerializer(hub).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Reports & AI ─────────────────────────────────────────────────────


class AdminReportListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Reports"],
        summary="List reports",
        description="Retrieve paginated list of AI-generated situation reports.",
        parameters=[
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False, description="Filter by hub ID"),
            OpenApiParameter("is_auto", bool, OpenApiParameter.QUERY, required=False, description="Filter by auto-generated only"),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False, description="Page number"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="Results per page (max 100)"),
        ],
        responses={200: dict},
    )
    def get(self, request):
        try:
            service = AdminReportService()
            qs = service.list_reports(
                hub_id=request.query_params.get("hub_id"),
                is_auto=request.query_params.get("is_auto"),
            )
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            data = [
                {
                    "id": r.id,
                    "hub": r.hub_id,
                    "summary": r.summary,
                    "generated_by": r.generated_by,
                    "is_auto": r.is_auto,
                    "created_at": r.created_at.isoformat(),
                }
                for r in page
            ]
            return paginator.get_paginated_response(data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminReportDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Reports"],
        summary="Get report details",
        description="Retrieve full details of a specific situation report.",
        responses={200: dict},
    )
    def get(self, request, report_id):
        try:
            service = AdminReportService()
            r = service.get_report(report_id)
            return success_response(
                {
                    "id": r.id,
                    "hub": r.hub_id,
                    "summary": r.summary,
                    "generated_by": r.generated_by,
                    "is_auto": r.is_auto,
                    "created_at": r.created_at.isoformat(),
                    "pdf_file": r.pdf_file.url if r.pdf_file else None,
                }
            )
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminAIConfigView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "AI"],
        summary="Get AI config",
        description="Retrieve the current AI configuration settings.",
        responses={200: AIConfigSerializer},
    )
    def get(self, request):
        try:
            service = AdminReportService()
            config = service.get_ai_config()
            serializer = AIConfigSerializer(config)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        tags=["admin", "AI"],
        summary="Update AI config",
        description="Update AI configuration settings.",
        request=AIConfigSerializer,
        responses={200: AIConfigSerializer},
    )
    def put(self, request):
        try:
            service = AdminReportService()
            config = service.update_ai_config(request.data)
            serializer = AIConfigSerializer(config)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Messages ─────────────────────────────────────────────────────────


class AdminMessageListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Messages"],
        summary="List messages",
        description="Retrieve paginated list of inbound messages (WhatsApp/SMS) with optional filters.",
        parameters=[
            OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False, enum=MESSAGE_STATUSES, description="Filter by message status"),
            OpenApiParameter("source", str, OpenApiParameter.QUERY, required=False, enum=MESSAGE_SOURCES, description="Filter by message source"),
            OpenApiParameter("search", str, OpenApiParameter.QUERY, required=False, description="Search by sender number or message body"),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False, description="Page number"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="Results per page (max 100)"),
        ],
        responses={200: InboundMessageAdminSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = AdminMessageService()
            qs = service.list_messages(
                status=request.query_params.get("status"),
                source=request.query_params.get("source"),
                search=request.query_params.get("search"),
            )
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = InboundMessageAdminSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminMessageDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Messages"],
        summary="Get message details",
        description="Retrieve full details of a specific inbound message.",
        responses={200: InboundMessageAdminSerializer},
    )
    def get(self, request, msg_id):
        try:
            service = AdminMessageService()
            msg = service.get_message(msg_id)
            serializer = InboundMessageAdminSerializer(msg)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminMessageClassifyView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Messages"],
        summary="Classify message",
        description="Link an inbound message to a hazard for classification.",
        request=dict,
        responses={200: InboundMessageAdminSerializer},
        examples=[
            OpenApiExample(
                "Classify Message Example",
                value={"hazard_id": 1},
                request_only=True,
            ),
        ],
    )
    def patch(self, request, msg_id):
        try:
            hazard_id = request.data.get("hazard_id")
            service = AdminMessageService()
            msg = service.classify_message(msg_id, hazard_id)
            serializer = InboundMessageAdminSerializer(msg)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
