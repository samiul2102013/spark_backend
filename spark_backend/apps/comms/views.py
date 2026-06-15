from drf_spectacular.utils import OpenApiParameter, extend_schema
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


class CheckInView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["mobile"], request=CheckInCreateSerializer, responses={201: CheckInSerializer})
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
        tags=["mobile"],
        parameters=[
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("date", str, OpenApiParameter.QUERY, required=False),
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

    @extend_schema(tags=["mobile"], responses={200: CheckInSerializer})
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
        tags=["mobile"],
        parameters=[
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False),
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

    @extend_schema(tags=["mobile"], request=BroadcastCreateSerializer, responses={201: BroadcastSerializer})
    def post(self, request):
        try:
            hub_id = request.data.get("hub")
            if not hub_id:
                return error_response("hub is required.", http_status=status.HTTP_400_BAD_REQUEST)
            serializer = BroadcastCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = BroadcastService()
            broadcast = service.create_broadcast(hub_id, serializer.validated_data, sender=request.user)
            return created_response(BroadcastSerializer(broadcast).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BroadcastReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["mobile"], responses={200: dict})
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
        tags=["mobile"],
        parameters=[
            OpenApiParameter("unread_only", bool, OpenApiParameter.QUERY, required=False),
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

    @extend_schema(tags=["mobile"], responses={200: NotificationSerializer})
    def patch(self, request, notification_id):
        try:
            service = NotificationService()
            notification = service.mark_read(notification_id, request.user)
            return success_response(NotificationSerializer(notification).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationReadAllView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["mobile"], responses={200: dict})
    def post(self, request):
        try:
            service = NotificationService()
            result = service.mark_all_read(request.user)
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
