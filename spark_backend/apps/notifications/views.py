from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.responses import created_response, error_response

from .models import DeviceToken
from .serializers import DeviceTokenSerializer


class DeviceRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Notifications"],
        summary="Register device token",
        description="Register or update a Firebase Cloud Messaging device token for the authenticated user.",
        request=DeviceTokenSerializer,
        responses={201: DeviceTokenSerializer},
    )
    def post(self, request):
        try:
            token = request.data.get("token")
            platform = request.data.get("platform", "android")
            if not token:
                return error_response("token is required.", http_status=status.HTTP_400_BAD_REQUEST)
            obj, created = DeviceToken.objects.update_or_create(
                token=token,
                defaults={"user": request.user, "platform": platform},
            )
            serializer = DeviceTokenSerializer(obj)
            if created:
                return created_response(serializer.data)
            return created_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceUnregisterView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Notifications"],
        summary="Unregister device token",
        description="Remove a Firebase Cloud Messaging device token for the authenticated user.",
    )
    def delete(self, request):
        try:
            token = request.data.get("token")
            if not token:
                return error_response("token is required.", http_status=status.HTTP_400_BAD_REQUEST)
            deleted, _ = DeviceToken.objects.filter(token=token, user=request.user).delete()
            if deleted:
                from core.responses import success_response
                return success_response({"message": "Device token removed."})
            return error_response("Token not found.", http_status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
