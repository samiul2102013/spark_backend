from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.users.permissions import IsAdmin
from core.responses import created_response, deleted_response, error_response, success_response

from .serializers import HubCoordinatorSerializer, HubSerializer, HubStatusSerializer
from .services import HubService


@extend_schema(
    parameters=[
        OpenApiParameter(
            "status",
            str,
            OpenApiParameter.QUERY,
            required=False,
            description="Filter by hub status",
        )
    ],
    responses={200: HubSerializer(many=True)},
    tags=["hubs"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def hub_list_view(request):
    status_filter = request.query_params.get("status")
    hubs = HubService.list_hubs(status=status_filter)
    return success_response(HubSerializer(hubs, many=True).data)


@extend_schema(
    responses={200: HubSerializer},
    tags=["hubs"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def hub_detail_view(request, hub_id):
    hub = HubService.get_hub(hub_id)
    return success_response(HubSerializer(hub).data)


@extend_schema(
    request=HubSerializer,
    responses={201: HubSerializer},
    tags=["hubs"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def hub_create_view(request):
    serializer = HubSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    hub = HubService.create_hub(serializer.validated_data)
    return created_response(HubSerializer(hub).data)


@extend_schema(
    request=HubSerializer,
    responses={200: HubSerializer},
    tags=["hubs"],
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsAdmin])
def hub_update_view(request, hub_id):
    serializer = HubSerializer(data=request.data, partial=True)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    hub = HubService.update_hub(hub_id, serializer.validated_data)
    return success_response(HubSerializer(hub).data)


@extend_schema(
    responses={204: None},
    tags=["hubs"],
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdmin])
def hub_delete_view(request, hub_id):
    HubService.delete_hub(hub_id)
    return deleted_response()


@extend_schema(
    request=HubStatusSerializer,
    responses={200: HubSerializer},
    tags=["hubs"],
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def hub_status_update_view(request, hub_id):
    serializer = HubStatusSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    status_val = data.pop("status")
    hub = HubService.update_status(hub_id, status_val, extra=data)
    return success_response(HubSerializer(hub).data)


@extend_schema(
    request=HubCoordinatorSerializer,
    responses={200: HubSerializer},
    tags=["hubs"],
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsAdmin])
def hub_assign_coordinator_view(request, hub_id):
    serializer = HubCoordinatorSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    hub = HubService.assign_coordinator(hub_id, serializer.validated_data["coordinator_id"])
    return success_response(HubSerializer(hub).data)
