from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.users.permissions import IsAdmin, IsAdminOrCoordinator
from core.pagination import StandardPagination
from core.responses import created_response, deleted_response, error_response, success_response

from .serializers import (
    HubCoordinatorSerializer,
    HubListSerializer,
    HubSerializer,
    HubStatusSerializer,
)
from .services import HubService


class HubListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["mobile"],
        parameters=[
            OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False),
        ],
        responses={200: HubListSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = HubService()
            qs = service.list_hubs(status=request.query_params.get("status"))
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = HubListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(tags=["mobile"], request=HubSerializer, responses={201: HubSerializer})
    def post(self, request):
        try:
            self.permission_classes = [IsAuthenticated, IsAdmin]
            self.check_permissions(request)
            serializer = HubSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = HubService()
            hub = service.create_hub(serializer.validated_data)
            return created_response(HubSerializer(hub).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HubDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["mobile"], responses={200: HubSerializer})
    def get(self, request, hub_id):
        try:
            service = HubService()
            hub = service.get_hub(hub_id)
            return success_response(HubSerializer(hub).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(tags=["mobile"], request=HubSerializer, responses={200: HubSerializer})
    def put(self, request, hub_id):
        try:
            self.permission_classes = [IsAuthenticated, IsAdmin]
            self.check_permissions(request)
            serializer = HubSerializer(data=request.data, partial=True)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = HubService()
            hub = service.update_hub(hub_id, serializer.validated_data)
            return success_response(HubSerializer(hub).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(tags=["mobile"], responses={204: None})
    def delete(self, request, hub_id):
        try:
            self.permission_classes = [IsAuthenticated, IsAdmin]
            self.check_permissions(request)
            service = HubService()
            service.delete_hub(hub_id)
            return deleted_response()
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HubStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrCoordinator]

    @extend_schema(tags=["mobile"], request=HubStatusSerializer, responses={200: HubSerializer})
    def patch(self, request, hub_id):
        try:
            serializer = HubStatusSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            data = serializer.validated_data
            status_val = data.pop("status")
            service = HubService()
            hub = service.update_status(hub_id, status_val, extra=data)
            return success_response(HubSerializer(hub).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HubCoordinatorView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["mobile"], request=HubCoordinatorSerializer, responses={200: HubSerializer}
    )
    def patch(self, request, hub_id):
        try:
            serializer = HubCoordinatorSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = HubService()
            hub = service.assign_coordinator(hub_id, serializer.validated_data["coordinator_id"])
            return success_response(HubSerializer(hub).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HubCheckinsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrCoordinator]

    @extend_schema(
        tags=["mobile"],
        parameters=[
            OpenApiParameter("date", str, OpenApiParameter.QUERY, required=False),
        ],
        responses={200: dict},
    )
    def get(self, request, hub_id):
        try:
            service = HubService()
            checkins = service.get_hub_checkins(hub_id, date=request.query_params.get("date"))
            from apps.comms.serializers import CheckInSerializer

            serializer = CheckInSerializer(checkins, many=True)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HubBroadcastsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["mobile"], responses={200: dict})
    def get(self, request, hub_id):
        try:
            service = HubService()
            broadcasts = service.get_hub_broadcasts(hub_id)
            from apps.comms.serializers import BroadcastSerializer

            serializer = BroadcastSerializer(broadcasts, many=True)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HubResourcesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["mobile"], responses={200: dict})
    def get(self, request, hub_id):
        try:
            service = HubService()
            resources = service.get_hub_resources(hub_id)
            return success_response(resources)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
