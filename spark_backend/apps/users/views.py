from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from core.responses import created_response, error_response, success_response

from .blacklist import blacklist_refresh_token, is_token_blacklisted
from .serializers import (
    AcceptInviteSerializer,
    BiometricLoginSerializer,
    BiometricRegisterSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    OTPSendSerializer,
    OTPVerifySerializer,
    ProfileSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
)
from .services import AuthService


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["mobile"], request=RegisterSerializer, responses={201: None})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            service = AuthService()
            result = service.register(**serializer.validated_data)
            return created_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)


class OTPSendView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["mobile"], request=OTPSendSerializer, responses={200: None})
    def post(self, request):
        serializer = OTPSendSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            service = AuthService()
            result = service.send_otp(**serializer.validated_data)
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["mobile"], request=OTPVerifySerializer, responses={200: None})
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            service = AuthService()
            result = service.verify_otp(**serializer.validated_data)
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["mobile"], request=LoginSerializer, responses={200: None})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            service = AuthService()
            result = service.login(**serializer.validated_data)
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["mobile"], request=LogoutSerializer, responses={200: None})
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            blacklist_refresh_token(serializer.validated_data["refresh"])
            return success_response({"message": "Logged out successfully."})
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BiometricRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["mobile"], request=BiometricRegisterSerializer, responses={200: None})
    def post(self, request):
        serializer = BiometricRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            service = AuthService()
            result = service.register_biometric(request.user, serializer.validated_data["key"])
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BiometricLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["mobile"], request=BiometricLoginSerializer, responses={200: None})
    def post(self, request):
        serializer = BiometricLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            service = AuthService()
            result = service.biometric_login(**serializer.validated_data)
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)


class OfflineTokenView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["mobile"], responses={200: None})
    def post(self, request):
        try:
            service = AuthService()
            result = service.issue_offline_token(request.user)
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InviteValidateView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["mobile"], responses={200: None})
    def post(self, request, token):
        try:
            service = AuthService()
            result = service.validate_invite(token)
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)


class InviteAcceptView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["mobile"], request=AcceptInviteSerializer, responses={200: None})
    def post(self, request):
        serializer = AcceptInviteSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            service = AuthService()
            result = service.accept_invite(**serializer.validated_data)
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["mobile"], request=ForgotPasswordSerializer, responses={200: None})
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            service = AuthService()
            result = service.forgot_password(**serializer.validated_data)
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["mobile"], request=ResetPasswordSerializer, responses={200: None})
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            service = AuthService()
            result = service.reset_password(**serializer.validated_data)
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["mobile"], responses={200: ProfileSerializer})
    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return success_response(serializer.data)

    @extend_schema(tags=["mobile"], request=ProfileSerializer, responses={200: ProfileSerializer})
    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            service = AuthService()
            user = service.update_profile(request.user, serializer.validated_data)
            return success_response(ProfileSerializer(user).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["mobile"], request=ChangePasswordSerializer, responses={200: None})
    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            service = AuthService()
            result = service.change_password(
                request.user,
                serializer.validated_data["old_password"],
                serializer.validated_data["new_password"],
            )
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BlacklistCheckTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh = request.data.get("refresh")
        if refresh and is_token_blacklisted(refresh):
            return error_response(
                "Token has been blacklisted.", http_status=status.HTTP_401_UNAUTHORIZED
            )
        return super().post(request, *args, **kwargs)
