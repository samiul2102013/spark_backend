from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from core.responses import error_response, success_response

from .models import StaticContent
from .serializers import StaticContentSerializer


class PrivacyPolicyView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["mobile", "Content"],
        summary="Get privacy policy",
        description="Retrieve the privacy policy content.",
        responses={200: StaticContentSerializer},
    )
    def get(self, request):
        try:
            obj = StaticContent.objects.get(slug="privacy-policy")
            serializer = StaticContentSerializer(obj)
            return success_response(serializer.data)
        except StaticContent.DoesNotExist:
            return error_response(
                "Privacy policy not found.", http_status=status.HTTP_404_NOT_FOUND
            )


class TermsView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["mobile", "Content"],
        summary="Get terms and conditions",
        description="Retrieve the terms and conditions content.",
        responses={200: StaticContentSerializer},
    )
    def get(self, request):
        try:
            obj = StaticContent.objects.get(slug="terms-and-conditions")
            serializer = StaticContentSerializer(obj)
            return success_response(serializer.data)
        except StaticContent.DoesNotExist:
            return error_response(
                "Terms and conditions not found.", http_status=status.HTTP_404_NOT_FOUND
            )
