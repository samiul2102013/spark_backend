from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView

from core.responses import created_response, error_response, success_response

from .blacklist import blacklist_refresh_token, is_token_blacklisted
from .permissions import IsAdmin
from .serializers import (
    AcceptInviteSerializer,
    BiometricLoginSerializer,
    BiometricRegisterSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    InviteGovernmentSerializer,
    LoginSerializer,
    LogoutSerializer,
    OTPSendSerializer,
    OTPVerifySerializer,
    ProfileSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    SetRoleSerializer,
)
from .services import AuthService


@extend_schema(
    request=RegisterSerializer,
    responses={201: None},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    result = AuthService.register(**serializer.validated_data)
    return created_response(result)


@extend_schema(
    request=OTPSendSerializer,
    responses={200: None},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def otp_send_view(request):
    serializer = OTPSendSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    result = AuthService.send_otp(**serializer.validated_data)
    return success_response(result)


@extend_schema(
    request=OTPVerifySerializer,
    responses={200: None},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def otp_verify_view(request):
    serializer = OTPVerifySerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    result = AuthService.verify_otp(**serializer.validated_data)
    return success_response(result)


@extend_schema(
    request=LoginSerializer,
    responses={200: None},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    result = AuthService.login(**serializer.validated_data)
    return success_response(result)


@extend_schema(
    request=BiometricRegisterSerializer,
    responses={200: None},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def biometric_register_view(request):
    serializer = BiometricRegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    result = AuthService.register_biometric(request.user, serializer.validated_data["key"])
    return success_response(result)


@extend_schema(
    request=BiometricLoginSerializer,
    responses={200: None},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def biometric_login_view(request):
    serializer = BiometricLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    result = AuthService.biometric_login(**serializer.validated_data)
    return success_response(result)


@extend_schema(
    request=None,
    responses={200: None},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def offline_token_view(request):
    result = AuthService.issue_offline_token(request.user)
    return success_response(result)


@extend_schema(
    parameters=[OpenApiParameter("token", str, OpenApiParameter.PATH)],
    request=None,
    responses={200: None},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def invite_validate_view(request, token):
    result = AuthService.validate_invite(token)
    return success_response(result)


@extend_schema(
    request=AcceptInviteSerializer,
    responses={200: None},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def invite_accept_view(request):
    serializer = AcceptInviteSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    result = AuthService.accept_invite(**serializer.validated_data)
    return success_response(result)


@extend_schema(
    request=InviteGovernmentSerializer,
    responses={200: None},
    tags=["admin"],
)
@api_view(["POST"])
@permission_classes([IsAdmin])
def invite_government_view(request):
    serializer = InviteGovernmentSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    result = AuthService.invite_government(**serializer.validated_data)
    return success_response(result)


@extend_schema(
    request=ForgotPasswordSerializer,
    responses={200: None},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password_view(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    result = AuthService.forgot_password(**serializer.validated_data)
    return success_response(result)


@extend_schema(
    request=ResetPasswordSerializer,
    responses={200: None},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_view(request):
    serializer = ResetPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    result = AuthService.reset_password(**serializer.validated_data)
    return success_response(result)


@extend_schema(
    request=ProfileSerializer,
    responses={200: ProfileSerializer},
    tags=["users"],
)
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    if request.method == "GET":
        serializer = ProfileSerializer(request.user)
        return success_response(serializer.data)

    serializer = ProfileSerializer(request.user, data=request.data, partial=True)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    user = AuthService.update_profile(request.user, serializer.validated_data)
    return success_response(ProfileSerializer(user).data)


@extend_schema(
    request=ChangePasswordSerializer,
    responses={200: None},
    tags=["users"],
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    result = AuthService.change_password(
        request.user,
        serializer.validated_data["old_password"],
        serializer.validated_data["new_password"],
    )
    return success_response(result)


@extend_schema(
    parameters=[
        OpenApiParameter(
            "user_id", str, OpenApiParameter.PATH, description="phone_number or username"
        )
    ],
    request=SetRoleSerializer,
    responses={200: None},
    tags=["admin"],
)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def set_role_view(request, user_id):
    serializer = SetRoleSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    user_model = get_user_model()
    user_id = user_id.strip('"')
    target_user = (
        user_model.objects.filter(phone_number=user_id).first()
        or user_model.objects.filter(username=user_id).first()
    )
    if not target_user:
        return error_response("User not found.", http_status=status.HTTP_404_NOT_FOUND)
    result = AuthService.set_role(target_user, serializer.validated_data["role"])
    return success_response(result)


@extend_schema(
    request=LogoutSerializer,
    responses={200: None},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def logout_view(request):
    serializer = LogoutSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    blacklist_refresh_token(serializer.validated_data["refresh"])
    return success_response({"message": "Logged out successfully."})


class BlacklistCheckTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh = request.data.get("refresh")
        if refresh and is_token_blacklisted(refresh):
            return error_response(
                "Token has been blacklisted.", http_status=status.HTTP_401_UNAUTHORIZED
            )
        return super().post(request, *args, **kwargs)
