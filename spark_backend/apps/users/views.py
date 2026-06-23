from drf_spectacular.utils import OpenApiExample, extend_schema
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
    SetPasswordSerializer,
    VerifyResetOTPSerializer,
)
from .services import AuthService


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["mobile", "Auth"],
        summary="Register a new user",
        description="Create a new resident account via OTP registration.",
        request=RegisterSerializer,
        responses={201: None},
        examples=[
            OpenApiExample(
                "Register Example",
                value={
                    "phone": "01856669533",
                    "full_name": "John Doe",
                    "household_size": 4,
                    "medical_needs": "None",
                    "latitude": 18.1096,
                    "longitude": -77.2975,
                },
                request_only=True,
            ),
        ],
    )
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

    @extend_schema(
        tags=["mobile", "Auth"],
        summary="Send OTP code",
        description="Send a 6-digit OTP code to the given phone number for verification.",
        request=OTPSendSerializer,
        responses={200: None},
        examples=[
            OpenApiExample(
                "Send OTP Example",
                value={"phone": "01856669533"},
                request_only=True,
            ),
        ],
    )
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

    @extend_schema(
        tags=["mobile", "Auth"],
        summary="Verify OTP code",
        description="Verify the 6-digit OTP code. Returns access and refresh tokens on success.",
        request=OTPVerifySerializer,
        responses={200: None},
        examples=[
            OpenApiExample(
                "Verify OTP Example",
                value={"phone": "01856669533", "code": "123456"},
                request_only=True,
            ),
        ],
    )
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

    @extend_schema(
        tags=["mobile", "dashboard", "Auth"],
        summary="Login with credentials",
        description="Authenticate with email/username and password. Returns access and refresh JWT tokens.",
        request=LoginSerializer,
        responses={200: None},
        examples=[
            OpenApiExample(
                "Login Example",
                value={"username": "john@example.com", "password": "password123"},
                request_only=True,
            ),
        ],
    )
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

    @extend_schema(
        tags=["mobile", "Auth"],
        summary="Logout",
        description="Blacklist the refresh token to invalidate the session.",
        request=LogoutSerializer,
        responses={200: None},
        examples=[
            OpenApiExample(
                "Logout Example",
                value={"refresh": "eyJhbGciOiJIUzI1NiJ9..."},
                request_only=True,
            ),
        ],
    )
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

    @extend_schema(
        tags=["mobile", "Auth"],
        summary="Register biometric key",
        description="Register a biometric key for the authenticated user.",
        request=BiometricRegisterSerializer,
        responses={200: None},
        examples=[
            OpenApiExample(
                "Biometric Register Example",
                value={"key": "device-biometric-key-here"},
                request_only=True,
            ),
        ],
    )
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

    @extend_schema(
        tags=["mobile", "Auth"],
        summary="Biometric login",
        description="Login using a biometric key instead of password.",
        request=BiometricLoginSerializer,
        responses={200: None},
        examples=[
            OpenApiExample(
                "Biometric Login Example",
                value={"key": "device-biometric-key-here"},
                request_only=True,
            ),
        ],
    )
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

    @extend_schema(
        tags=["mobile", "Auth"],
        summary="Issue offline token",
        description="Generate an offline token for the authenticated user to use when connectivity is limited.",
        responses={200: None},
    )
    def post(self, request):
        try:
            service = AuthService()
            result = service.issue_offline_token(request.user)
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InviteValidateView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["mobile", "dashboard", "Invites"],
        summary="Validate invite token",
        description="Check if an invite token is valid and return invite details.",
        responses={200: None},
    )
    def post(self, request, token):
        try:
            service = AuthService()
            result = service.validate_invite(token)
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)


class InviteAcceptView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["mobile", "dashboard", "Invites"],
        summary="Accept invite",
        description="Accept a government/coordinator invite by setting a password. Returns JWT tokens on success.",
        request=AcceptInviteSerializer,
        responses={200: None},
        examples=[
            OpenApiExample(
                "Accept Invite Example",
                value={
                    "token": "invite-token-here",
                    "password": "securePassword123",
                    "confirm_password": "securePassword123",
                },
                request_only=True,
            ),
        ],
    )
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

    @extend_schema(
        tags=["mobile", "dashboard", "Auth"],
        summary="Forgot password",
        description="Request a password reset code. Sends reset code to the user's phone or email.",
        request=ForgotPasswordSerializer,
        responses={200: None},
        examples=[
            OpenApiExample(
                "Forgot Password Example",
                value={"identifier": "01856669533"},
                request_only=True,
            ),
        ],
    )
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


class VerifyResetOTPView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["mobile", "dashboard", "Auth"],
        summary="Verify reset OTP",
        description="Verify the 6-digit OTP sent to email/phone during forgot-password. Returns an access token on success to use in the reset-password step.",
        request=VerifyResetOTPSerializer,
        responses={200: None},
        examples=[
            OpenApiExample(
                "Verify Reset OTP Example",
                value={"identifier": "gov@example.com", "code": "123456"},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = VerifyResetOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            service = AuthService()
            result = service.verify_reset_otp(**serializer.validated_data)
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "dashboard", "Auth"],
        summary="Reset password",
        description="Set a new password for the authenticated user. No old password required.",
        request=ResetPasswordSerializer,
        responses={200: None},
        examples=[
            OpenApiExample(
                "Reset Password Example",
                value={
                    "new_password": "newSecurePass123",
                    "confirm_password": "newSecurePass123",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            service = AuthService()
            result = service.reset_password(
                user=request.user, new_password=serializer.validated_data["new_password"]
            )
            return success_response(result)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Profile"],
        summary="Get profile",
        description="Retrieve the authenticated user's profile information.",
        responses={200: ProfileSerializer},
    )
    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return success_response(serializer.data)

    @extend_schema(
        tags=["mobile", "Profile"],
        summary="Update profile",
        description="Partially update the authenticated user's profile fields.",
        request=ProfileSerializer,
        responses={200: ProfileSerializer},
        examples=[
            OpenApiExample(
                "Update Profile Example",
                value={"full_name": "Jane Doe", "household_size": 3, "medical_needs": "Asthma"},
                request_only=True,
            ),
        ],
    )
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

    @extend_schema(
        tags=["mobile", "dashboard", "Profile"],
        summary="Change password",
        description="Change the authenticated user's password by providing the old password.",
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


class SetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Profile"],
        summary="Set password",
        description="Set a new password for the authenticated user (no old password required).",
        request=SetPasswordSerializer,
        responses={200: None},
        examples=[
            OpenApiExample(
                "Set Password Example",
                value={"new_password": "newSecurePass456", "confirm_password": "newSecurePass456"},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        try:
            service = AuthService()
            result = service.set_password(request.user, serializer.validated_data["new_password"])
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
