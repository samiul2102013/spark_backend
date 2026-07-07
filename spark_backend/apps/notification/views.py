from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.pagination import StandardPagination
from core.responses import created_response, error_response, success_response

from .models import FCMToken
from .serializers import FCMTokenSerializer, NotificationSerializer
from .services.notification_service import NotificationService


class DeviceRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Notifications"],
        summary="Register device token",
        request=FCMTokenSerializer,
        responses={201: FCMTokenSerializer},
    )
    def post(self, request):
        try:
            token = request.data.get("token")
            platform = request.data.get("platform", "android")
            if not token:
                return error_response("token is required.", http_status=status.HTTP_400_BAD_REQUEST)
            obj, created = FCMToken.objects.update_or_create(
                token=token,
                defaults={"user": request.user, "platform": platform, "is_active": True},
            )
            serializer = FCMTokenSerializer(obj)
            return created_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceUnregisterView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Notifications"],
        summary="Unregister device token",
    )
    def delete(self, request):
        try:
            token = request.data.get("token")
            if not token:
                return error_response("token is required.", http_status=status.HTTP_400_BAD_REQUEST)
            updated = FCMToken.objects.filter(token=token, user=request.user).update(is_active=False)
            if updated:
                return success_response({"message": "Device token deactivated."})
            return error_response("Token not found.", http_status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Notifications"],
        summary="List notifications",
        parameters=[
            OpenApiParameter("unread_only", bool, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False),
        ],
        responses={200: NotificationSerializer(many=True)},
    )
    def get(self, request):
        try:
            unread_only = request.query_params.get("unread_only", "").lower() in ("true", "1")
            qs = NotificationService.list_notifications(request.user, unread_only=unread_only)
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
        responses={200: NotificationSerializer},
    )
    def patch(self, request, notification_id):
        try:
            notification = NotificationService.mark_read(notification_id, request.user)
            return success_response(NotificationSerializer(notification).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationReadAllView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Notifications"],
        summary="Mark all notifications as read",
        responses={200: dict},
    )
    def post(self, request):
        try:
            result = NotificationService.mark_all_read(request.user)
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
