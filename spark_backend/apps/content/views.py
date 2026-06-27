from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.users.permissions import IsAdmin
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


class AdminPrivacyPolicyView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Content"],
        summary="Get privacy policy",
        description="Retrieve the privacy policy content (admin).",
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

    @extend_schema(
        tags=["admin", "Content"],
        summary="Update privacy policy",
        description="Update the privacy policy content (admin only).",
        request=StaticContentSerializer,
        responses={200: StaticContentSerializer},
    )
    def patch(self, request):
        try:
            obj, _ = StaticContent.objects.get_or_create(
                slug="privacy-policy",
                defaults={"title": "Privacy Policy", "content": ""},
            )
            serializer = StaticContentSerializer(obj, data=request.data, partial=True)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminTermsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["admin", "Content"],
        summary="Get terms and conditions",
        description="Retrieve the terms and conditions content (admin).",
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

    @extend_schema(
        tags=["admin", "Content"],
        summary="Update terms and conditions",
        description="Update the terms and conditions content (admin only).",
        request=StaticContentSerializer,
        responses={200: StaticContentSerializer},
    )
    def patch(self, request):
        try:
            obj, _ = StaticContent.objects.get_or_create(
                slug="terms-and-conditions",
                defaults={"title": "Terms and Conditions", "content": ""},
            )
            serializer = StaticContentSerializer(obj, data=request.data, partial=True)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
