from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.users.permissions import IsAdminOrCoordinator
from core.pagination import StandardPagination
from core.responses import created_response, error_response, success_response

from .serializers import (
    BroadcastCreateSerializer,
    BroadcastSerializer,
    CheckInCreateSerializer,
    CheckInSerializer,
    NotificationSerializer,
)
from .services import BroadcastService, CheckInService, NotificationService

CHECKIN_STATUSES = ["safe", "need_assistance"]
BROADCAST_PRIORITIES = ["info", "warning", "urgent"]


class CheckInView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Check-Ins"],
        summary="Create check-in",
        description="Submit a safety check-in at a hub. The user is auto-set to the authenticated user.",
        request=CheckInCreateSerializer,
        responses={201: CheckInSerializer},
        examples=[
            OpenApiExample(
                "Check-In Example",
                value={
                    "hub": 1,
                    "status": "safe",
                    "people_count": 3,
                    "road_access": "open",
                    "medical_notes": "No issues",
                    "latitude": 18.1096,
                    "longitude": -77.2975,
                    "client_uuid": "uuid-string-here",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        try:
            serializer = CheckInCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = CheckInService()
            checkin = service.create_checkin(serializer.validated_data, user=request.user)
            return created_response(CheckInSerializer(checkin).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckInHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Check-Ins"],
        summary="List check-in history",
        description="Retrieve paginated check-in history for the authenticated user, with optional filters.",
        parameters=[
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False, description="Filter by hub ID"),
            OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False, enum=CHECKIN_STATUSES, description="Filter by status"),
            OpenApiParameter("date", str, OpenApiParameter.QUERY, required=False, description="Filter by date (YYYY-MM-DD)"),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False, description="Page number"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="Results per page (max 100)"),
        ],
        responses={200: CheckInSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = CheckInService()
            qs = service.list_checkins(
                user=request.user,
                hub_id=request.query_params.get("hub_id"),
                status=request.query_params.get("status"),
                date=request.query_params.get("date"),
            )
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = CheckInSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckInLatestView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Check-Ins"],
        summary="Get latest check-in",
        description="Retrieve the most recent check-in for the authenticated user. Returns a single object, not paginated.",
        responses={200: CheckInSerializer},
    )
    def get(self, request):
        try:
            service = CheckInService()
            checkin = service.get_latest_checkin(request.user)
            if not checkin:
                return success_response(None)
            return success_response(CheckInSerializer(checkin).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BroadcastListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Broadcasts"],
        summary="List broadcasts",
        description="Retrieve paginated list of broadcasts, optionally filtered by hub.",
        parameters=[
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False, description="Filter by hub ID"),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False, description="Page number"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="Results per page (max 100)"),
        ],
        responses={200: BroadcastSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = BroadcastService()
            qs = service.list_broadcasts(hub_id=request.query_params.get("hub_id"))
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = BroadcastSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BroadcastCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrCoordinator]

    @extend_schema(
        tags=["mobile", "Broadcasts"],
        summary="Create broadcast",
        description="Create a new broadcast for a hub. The sender is auto-set to the authenticated user.",
        request=BroadcastCreateSerializer,
        responses={201: BroadcastSerializer},
        examples=[
            OpenApiExample(
                "Create Broadcast Example",
                value={
                    "hub": 1,
                    "subject": "Weather Advisory",
                    "body": "Heavy rainfall expected. Stay indoors.",
                    "priority": "warning",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        try:
            hub_id = request.data.get("hub")
            if not hub_id:
                return error_response("hub is required.", http_status=status.HTTP_400_BAD_REQUEST)
            serializer = BroadcastCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = BroadcastService()
            broadcast = service.create_broadcast(
                hub_id, serializer.validated_data, sender=request.user
            )
            return created_response(BroadcastSerializer(broadcast).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BroadcastReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Broadcasts"],
        summary="Mark broadcast as read",
        description="Mark a specific broadcast as read by the authenticated user.",
        responses={200: dict},
    )
    def post(self, request, broadcast_id):
        try:
            service = BroadcastService()
            service.mark_read(broadcast_id, request.user)
            return success_response({"message": "Marked as read."})
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Notifications"],
        summary="List notifications",
        description="Retrieve paginated list of notifications for the authenticated user.",
        parameters=[
            OpenApiParameter("unread_only", bool, OpenApiParameter.QUERY, required=False, description="Filter to only unread notifications"),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False, description="Page number"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="Results per page (max 100)"),
        ],
        responses={200: NotificationSerializer(many=True)},
    )
    def get(self, request):
        try:
            unread_only = request.query_params.get("unread_only", "").lower() in ("true", "1")
            service = NotificationService()
            qs = service.list_notifications(request.user, unread_only=unread_only)
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = NotificationSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Notifications"],
        summary="Mark notification as read",
        description="Mark a specific notification as read by ID.",
        responses={200: NotificationSerializer},
    )
    def patch(self, request, notification_id):
        try:
            service = NotificationService()
            notification = service.mark_read(notification_id, request.user)
            return success_response(NotificationSerializer(notification).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationReadAllView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Notifications"],
        summary="Mark all notifications as read",
        description="Mark all notifications for the authenticated user as read.",
        responses={200: dict},
    )
    def post(self, request):
        try:
            service = NotificationService()
            result = service.mark_all_read(request.user)
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
