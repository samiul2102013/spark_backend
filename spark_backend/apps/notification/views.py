from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.responses import created_response, error_response, success_response

from .models import FCMToken
from .serializers import FCMTokenSerializer


class DeviceRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Notifications"],
        summary="Register device token",
        description="Register or update a Firebase Cloud Messaging device token for push notifications.",
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
        description="Deactivate a Firebase Cloud Messaging device token for the authenticated user.",
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
