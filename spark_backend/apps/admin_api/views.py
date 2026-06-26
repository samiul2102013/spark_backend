from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.permissions import IsAdmin
from apps.users.serializers import ChangePasswordSerializer, ProfileSerializer
from apps.users.services import AuthService
from core.pagination import StandardPagination
from core.responses import created_response, error_response, success_response

from .serializers import (
    AdminHubDetailSerializer,
    AdminHubListSerializer,
    AdminOverviewSerializer,
    AdminProfileSerializer,
    AdminUserListSerializer,
    AssignCoordinatorSerializer,
    CoordinatorDetailSerializer,
    CoordinatorListSerializer,
    HubCreateSerializer,
    InviteUserSerializer,
    ReassignCoordinatorSerializer,
    ResidentDetailSerializer,
    ResidentListSerializer,
    RoleDetailSerializer,
    SuspendUserSerializer,
)
from .services import AdminHubService, AdminOverviewService, AdminUserService

HAZARD_CATEGORIES = [
    "flooding", "fallen_tree", "blocked_road", "utility_pole",
    "medical", "fire", "collapsed_building", "power_line_down",
    "landslide", "other",
]
HUB_STATUSES = ["open", "closed", "low_battery", "critical"]
USER_ROLES = ["resident", "coordinator", "government", "admin"]


# ─── Overview ─────────────────────────────────────────────────────────


class AdminOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Overview"],
        summary="Get admin overview",
        description="Aggregated platform statistics for the admin dashboard: check-ins, hubs, hazards, users, messages, urgent flags, and check-ins over time.",
        responses={200: AdminOverviewSerializer},
    )
    def get(self, request):
        try:
            service = AdminOverviewService()
            data = service.overview()
            return success_response(data)
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ── Residents ─────────────────────────────────────────────────────────


class AdminResidentListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Residents"],
        summary="List residents",
        description="Retrieve paginated list of all resident users with community, last check-in, and profile photo.",
        parameters=[
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("is_active", bool, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("search", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False),
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
            serializer = ResidentListSerializer(
                page, many=True, context={"request": request}
            )
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminResidentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Residents"],
        summary="Get resident details",
        description="Full resident details including community, last check-in, check-in count, and profile photo.",
        responses={200: ResidentDetailSerializer},
    )
    def get(self, request, user_id):
        try:
            service = AdminUserService()
            user = service.get_resident(user_id)
            serializer = ResidentDetailSerializer(user, context={"request": request})
            return success_response(serializer.data)
        except User.DoesNotExist:
            return error_response(
                "Resident not found", http_status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminResidentSuspendView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Residents"],
        summary="Suspend resident",
        description="Deactivate a resident account.",
        responses={200: ResidentListSerializer},
    )
    def patch(self, request, user_id):
        try:
            service = AdminUserService()
            user = service.suspend_user(user_id)
            return success_response(ResidentListSerializer(user).data)
        except User.DoesNotExist:
            return error_response(
                "Resident not found", http_status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminResidentActivateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Residents"],
        summary="Activate resident",
        description="Reactivate a suspended resident account.",
        responses={200: ResidentListSerializer},
    )
    def patch(self, request, user_id):
        try:
            service = AdminUserService()
            user = service.activate_user(user_id)
            return success_response(ResidentListSerializer(user).data)
        except User.DoesNotExist:
            return error_response(
                "Resident not found", http_status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ── Coordinators ──────────────────────────────────────────────────────


class AdminCoordinatorListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Coordinators"],
        summary="List coordinators",
        description="Retrieve paginated list of all coordinators.",
        parameters=[
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("is_active", bool, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("search", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False),
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
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminCoordinatorDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Coordinators"],
        summary="Get coordinator details",
        description="Full details of a specific coordinator.",
        responses={200: CoordinatorDetailSerializer},
    )
    def get(self, request, user_id):
        try:
            service = AdminUserService()
            user = service.get_coordinator(user_id)
            serializer = CoordinatorDetailSerializer(user)
            return success_response(serializer.data)
        except User.DoesNotExist:
            return error_response(
                "Coordinator not found", http_status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminCoordinatorSuspendView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Coordinators"],
        summary="Suspend coordinator",
        description="Deactivate a coordinator account.",
        responses={200: CoordinatorListSerializer},
    )
    def patch(self, request, user_id):
        try:
            service = AdminUserService()
            user = service.suspend_user(user_id)
            return success_response(CoordinatorListSerializer(user).data)
        except User.DoesNotExist:
            return error_response(
                "Coordinator not found", http_status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ── Users (Access Control) ────────────────────────────────────────────


class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Users"],
        summary="List all users",
        description="Retrieve paginated list of all platform users for access control.",
        parameters=[
            OpenApiParameter("role", str, OpenApiParameter.QUERY, required=False, enum=USER_ROLES),
            OpenApiParameter("is_active", bool, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("search", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False),
        ],
        responses={200: AdminUserListSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = AdminUserService()
            qs = service.list_all_users(
                role=request.query_params.get("role"),
                is_active=request.query_params.get("is_active"),
                search=request.query_params.get("search"),
            )
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = AdminUserListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminUserSuspendView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Users"],
        summary="Suspend any user",
        description="Deactivate any user account (resident, coordinator, government).",
        request=SuspendUserSerializer,
        responses={200: AdminUserListSerializer},
    )
    def patch(self, request, user_id):
        try:
            service = AdminUserService()
            user = service.suspend_user(user_id)
            return success_response(AdminUserListSerializer(user).data)
        except User.DoesNotExist:
            return error_response(
                "User not found", http_status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminUserActivateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Users"],
        summary="Activate any user",
        description="Reactivate a suspended user account.",
        responses={200: AdminUserListSerializer},
    )
    def patch(self, request, user_id):
        try:
            service = AdminUserService()
            user = service.activate_user(user_id)
            return success_response(AdminUserListSerializer(user).data)
        except User.DoesNotExist:
            return error_response(
                "User not found", http_status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminInviteUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Users"],
        summary="Invite user",
        description="Invite a new user (resident, coordinator, or government).",
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
                return error_response(
                    serializer.errors, http_status=status.HTTP_400_BAD_REQUEST
                )
            service = AdminUserService()
            user = service.invite_user(serializer.validated_data)
            return created_response(ProfileSerializer(user).data)
        except ValueError as e:
            return error_response(
                str(e), http_status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminInviteByEmailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "dashboard", "Users"],
        summary="Invite government user by email",
        description="Send an invitation email to a government user.",
        responses={201: None},
    )
    def post(self, request):
        from apps.users.serializers import InviteGovernmentSerializer

        serializer = InviteGovernmentSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                serializer.errors, http_status=status.HTTP_400_BAD_REQUEST
            )
        try:
            service = AuthService()
            result = service.invite_government(**serializer.validated_data)
            return created_response(result)
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_400_BAD_REQUEST
            )


class AdminSetRoleView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Users"],
        summary="Set user role",
        description="Change a user's role (e.g. resident to coordinator).",
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
        from apps.users.serializers import SetRoleSerializer

        serializer = SetRoleSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                serializer.errors, http_status=status.HTTP_400_BAD_REQUEST
            )
        try:
            service = AdminUserService()
            user = service.set_role(user_id, serializer.validated_data["role"])
            return success_response(RoleDetailSerializer(user).data)
        except ValueError as e:
            return error_response(
                str(e), http_status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return error_response(
                "User not found", http_status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ── Hubs ──────────────────────────────────────────────────────────────


class AdminHubListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Hubs"],
        summary="List hubs",
        description="Retrieve paginated list of all hubs.",
        parameters=[
            OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False, enum=HUB_STATUSES),
            OpenApiParameter("search", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False),
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
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminHubDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Hubs"],
        summary="Get hub details",
        description="Full hub detail with coordinator info, battery, starlink, last resident check-in, recent check-ins and hazards.",
        responses={200: AdminHubDetailSerializer},
    )
    def get(self, request, hub_id):
        try:
            service = AdminHubService()
            hub = service.get_hub(hub_id)
            serializer = AdminHubDetailSerializer(hub)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminHubCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Hubs"],
        summary="Create hub",
        description="Create a new hub with location and optional coordinator.",
        request=HubCreateSerializer,
        responses={201: AdminHubListSerializer},
        examples=[
            OpenApiExample(
                "Create Hub Example",
                value={
                    "name": "Port Antonio Hub",
                    "address": "10 Harbour Street",
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
                return error_response(
                    serializer.errors, http_status=status.HTTP_400_BAD_REQUEST
                )
            service = AdminHubService()
            hub = service.create_hub(serializer.validated_data)
            return created_response(AdminHubListSerializer(hub).data)
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminHubAssignCoordinatorView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Hubs"],
        summary="Assign coordinator to hub",
        description="Assign a coordinator to a hub by their phone number.",
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
                return error_response(
                    serializer.errors, http_status=status.HTTP_400_BAD_REQUEST
                )
            service = AdminHubService()
            hub = service.assign_coordinator(
                hub_id, serializer.validated_data["coordinator_id"]
            )
            return success_response(AdminHubListSerializer(hub).data)
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminHubReassignCoordinatorView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Hubs"],
        summary="Reassign coordinator",
        description="Replace the coordinator for a hub.",
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
                return error_response(
                    serializer.errors, http_status=status.HTTP_400_BAD_REQUEST
                )
            service = AdminHubService()
            hub = service.reassign_coordinator(
                hub_id, serializer.validated_data["new_coordinator_id"]
            )
            return success_response(AdminHubListSerializer(hub).data)
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ── Admin Profile ─────────────────────────────────────────────────────


class AdminProfileView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Profile"],
        summary="Get admin profile",
        description="Retrieve the admin's own profile information.",
        responses={200: AdminProfileSerializer},
    )
    def get(self, request):
        serializer = AdminProfileSerializer(request.user)
        return success_response(serializer.data)

    @extend_schema(
        tags=["admin", "Profile"],
        summary="Update admin profile",
        description="Update admin's own name, email, and phone number.",
        request=AdminProfileSerializer,
        responses={200: AdminProfileSerializer},
        examples=[
            OpenApiExample(
                "Update Admin Profile",
                value={
                    "full_name": "Admin Name",
                    "email": "admin@example.com",
                    "phone_number": "+1234567890",
                },
                request_only=True,
            ),
        ],
    )
    def patch(self, request):
        serializer = AdminProfileSerializer(
            request.user, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return error_response(
                serializer.errors, http_status=status.HTTP_400_BAD_REQUEST
            )
        try:
            for field, value in serializer.validated_data.items():
                setattr(request.user, field, value)
            request.user.save()
            return success_response(AdminProfileSerializer(request.user).data)
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Profile"],
        summary="Change admin password",
        description="Change password by providing old password, new password, and confirmation.",
        request=ChangePasswordSerializer,
        responses={200: None},
        examples=[
            OpenApiExample(
                "Change Password Example",
                value={
                    "old_password": "currentPass123",
                    "new_password": "newSecurePass456",
                    "confirm_password": "newSecurePass456",
                },
                request_only=True,
            ),
        ],
    )
    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                serializer.errors, http_status=status.HTTP_400_BAD_REQUEST
            )
        try:
            service = AuthService()
            result = service.change_password(
                request.user,
                serializer.validated_data["old_password"],
                serializer.validated_data["new_password"],
            )
            return success_response(result)
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_400_BAD_REQUEST
            )
