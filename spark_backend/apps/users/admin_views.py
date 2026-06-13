from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.responses import error_response, success_response

from apps.users.permissions import IsAdmin

from .serializers import ProfileSerializer
from .services import AuthService


@extend_schema(
    parameters=[
        OpenApiParameter("role", str, OpenApiParameter.QUERY, required=False),
        OpenApiParameter("search", str, OpenApiParameter.QUERY, required=False),
    ],
    responses={200: ProfileSerializer(many=True)},
    tags=["admin"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_list_view(request):
    role = request.query_params.get("role")
    search = request.query_params.get("search")
    users = AuthService.list_users(role=role, search=search)
    return success_response(ProfileSerializer(users, many=True).data)


@extend_schema(
    responses={200: ProfileSerializer},
    tags=["admin"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_detail_view(request, user_id):
    user = AuthService.get_user(user_id)
    return success_response(ProfileSerializer(user).data)


@extend_schema(
    request=ProfileSerializer,
    responses={200: ProfileSerializer},
    tags=["admin"],
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_update_view(request, user_id):
    serializer = ProfileSerializer(data=request.data, partial=True)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    user = AuthService.update_user(user_id, serializer.validated_data)
    return success_response(ProfileSerializer(user).data)


@extend_schema(
    responses={204: None},
    tags=["admin"],
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_delete_view(request, user_id):
    AuthService.delete_user(user_id)
    return success_response(None, message="User deleted", http_status=status.HTTP_204_NO_CONTENT)
