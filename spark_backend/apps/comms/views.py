from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.responses import created_response, error_response, success_response

from apps.users.permissions import IsResidentOrCoordinator

from .serializers import (
    BroadcastReadSerializer,
    BroadcastSerializer,
    CheckInSerializer,
    NotificationSerializer,
)
from .services import BroadcastReadService, BroadcastService, CheckInService, NotificationService


@extend_schema(
    parameters=[
        OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False),
    ],
    responses={200: CheckInSerializer(many=True)},
    tags=["comms"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def checkin_list_view(request):
    user = None if request.user.role == "admin" else request.user
    checkins = CheckInService.list_checkins(hub_id=request.query_params.get("hub_id"), user=user)
    return success_response(CheckInSerializer(checkins, many=True).data)


@extend_schema(
    request=CheckInSerializer,
    responses={201: CheckInSerializer},
    tags=["comms"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def checkin_create_view(request):
    serializer = CheckInSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    checkin = CheckInService.create_checkin(serializer.validated_data, user=request.user)
    return created_response(CheckInSerializer(checkin).data)


@extend_schema(
    parameters=[
        OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False),
    ],
    responses={200: BroadcastSerializer(many=True)},
    tags=["comms"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def broadcast_list_view(request):
    broadcasts = BroadcastService.list_broadcasts(hub_id=request.query_params.get("hub_id"))
    return success_response(BroadcastSerializer(broadcasts, many=True).data)


@extend_schema(
    request=BroadcastSerializer,
    responses={201: BroadcastSerializer},
    tags=["comms"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsResidentOrCoordinator])
def broadcast_create_view(request):
    serializer = BroadcastSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    broadcast = BroadcastService.create_broadcast(serializer.validated_data, sender=request.user)
    return created_response(BroadcastSerializer(broadcast).data)


@extend_schema(
    request=BroadcastReadSerializer,
    responses={200: BroadcastReadSerializer},
    tags=["comms"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def broadcast_mark_read_view(request, broadcast_id):
    read = BroadcastReadService.mark_read(broadcast_id, request.user)
    return success_response(BroadcastReadSerializer(read).data)


@extend_schema(
    parameters=[
        OpenApiParameter("unread_only", bool, OpenApiParameter.QUERY, required=False),
    ],
    responses={200: NotificationSerializer(many=True)},
    tags=["comms"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notification_list_view(request):
    unread_only = request.query_params.get("unread_only", "").lower() in ("true", "1")
    notifications = NotificationService.list_notifications(request.user, unread_only=unread_only)
    return success_response(NotificationSerializer(notifications, many=True).data)


@extend_schema(
    responses={200: NotificationSerializer},
    tags=["comms"],
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def notification_mark_read_view(request, notification_id):
    notification = NotificationService.mark_read(notification_id, request.user)
    return success_response(NotificationSerializer(notification).data)
