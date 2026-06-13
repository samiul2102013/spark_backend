from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import IsAdmin, IsResidentOrCoordinator
from core.responses import created_response, deleted_response, error_response, success_response

from .serializers import CommentSerializer, HazardSerializer
from .services import HazardService


@extend_schema(
    parameters=[
        OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False),
        OpenApiParameter("category", str, OpenApiParameter.QUERY, required=False),
        OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False),
    ],
    responses={200: HazardSerializer(many=True)},
    tags=["hazards"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def hazard_list_view(request):
    hazards = HazardService.list_hazards(
        status=request.query_params.get("status"),
        category=request.query_params.get("category"),
        hub_id=request.query_params.get("hub_id"),
    )
    return success_response(HazardSerializer(hazards, many=True).data)


@extend_schema(
    responses={200: HazardSerializer},
    tags=["hazards"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def hazard_detail_view(request, hazard_id):
    hazard = HazardService.get_hazard(hazard_id)
    return success_response(HazardSerializer(hazard).data)


@extend_schema(
    request=HazardSerializer,
    responses={201: HazardSerializer},
    tags=["hazards"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsResidentOrCoordinator])
def hazard_create_view(request):
    serializer = HazardSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    hazard = HazardService.create_hazard(serializer.validated_data, reporter=request.user)
    return created_response(HazardSerializer(hazard).data)


@extend_schema(
    request=HazardSerializer,
    responses={200: HazardSerializer},
    tags=["hazards"],
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsAdmin])
def hazard_update_view(request, hazard_id):
    serializer = HazardSerializer(data=request.data, partial=True)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    hazard = HazardService.update_hazard(hazard_id, serializer.validated_data)
    return success_response(HazardSerializer(hazard).data)


@extend_schema(
    responses={204: None},
    tags=["hazards"],
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdmin])
def hazard_delete_view(request, hazard_id):
    HazardService.delete_hazard(hazard_id)
    return deleted_response()


@extend_schema(
    parameters=[
        OpenApiParameter("hazard_id", int, OpenApiParameter.PATH),
    ],
    responses={200: CommentSerializer(many=True)},
    tags=["hazards"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def hazard_comment_list_view(request, hazard_id):
    comments = HazardService.list_comments(hazard_id)
    return success_response(CommentSerializer(comments, many=True).data)


@extend_schema(
    request=CommentSerializer,
    responses={201: CommentSerializer},
    tags=["hazards"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def hazard_comment_create_view(request, hazard_id):
    serializer = CommentSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    comment = HazardService.add_comment(
        hazard_id,
        serializer.validated_data["body"],
        author=request.user,
        photo=serializer.validated_data.get("photo"),
    )
    return created_response(CommentSerializer(comment).data)
