from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.users.permissions import IsDashboardUser
from core.pagination import StandardPagination
from core.responses import error_response, success_response

from .serializers import (
    AlertSerializer,
    HazardMapSerializer,
    HubMapSerializer,
    InfrastructureHubSerializer,
    OverviewSerializer,
    SituationReportSerializer,
)
from .services import DashboardService

HAZARD_SEVERITIES = [1, 2, 3]
HAZARD_STATUSES = ["active", "cleared"]


class DashboardOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsDashboardUser]

    @extend_schema(
        tags=["dashboard", "Overview"],
        summary="Get dashboard overview",
        description="Retrieve aggregate statistics for hubs, hazards, bookings, and check-ins.",
        responses={200: OverviewSerializer},
    )
    def get(self, request):
        try:
            service = DashboardService()
            data = service.overview()
            return success_response(data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardMapView(APIView):
    permission_classes = [IsAuthenticated, IsDashboardUser]

    @extend_schema(
        tags=["dashboard", "Map"],
        summary="Get map data",
        description="Retrieve hubs and hazards data for map display, optionally filtered by bounding box coordinates.",
        parameters=[
            OpenApiParameter("lat_min", float, OpenApiParameter.QUERY, required=False, description="Minimum latitude for bounding box"),
            OpenApiParameter("lat_max", float, OpenApiParameter.QUERY, required=False, description="Maximum latitude for bounding box"),
            OpenApiParameter("lng_min", float, OpenApiParameter.QUERY, required=False, description="Minimum longitude for bounding box"),
            OpenApiParameter("lng_max", float, OpenApiParameter.QUERY, required=False, description="Maximum longitude for bounding box"),
        ],
        responses={200: dict},
    )
    def get(self, request):
        try:
            bounds = {
                "lat_min": request.query_params.get("lat_min"),
                "lat_max": request.query_params.get("lat_max"),
                "lng_min": request.query_params.get("lng_min"),
                "lng_max": request.query_params.get("lng_max"),
            }
            service = DashboardService()
            data = service.map_data(bounds=bounds)
            hubs_serializer = HubMapSerializer(data["hubs"], many=True)
            hazards_serializer = HazardMapSerializer(data["hazards"], many=True)
            return success_response(
                {
                    "hubs": hubs_serializer.data,
                    "hazards": hazards_serializer.data,
                }
            )
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardReportsView(APIView):
    permission_classes = [IsAuthenticated, IsDashboardUser]

    @extend_schema(
        tags=["dashboard", "Reports"],
        summary="List situation reports",
        description="Retrieve paginated list of AI-generated situation reports, optionally filtered by hub.",
        parameters=[
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False, description="Filter by hub ID"),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False, description="Page number"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="Results per page (max 100)"),
        ],
        responses={200: SituationReportSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = DashboardService()
            qs = service.situation_reports(hub_id=request.query_params.get("hub_id"))
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = SituationReportSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardAlertsView(APIView):
    permission_classes = [IsAuthenticated, IsDashboardUser]

    @extend_schema(
        tags=["dashboard", "Alerts"],
        summary="List alerts",
        description="Retrieve paginated list of active hazard alerts for the dashboard.",
        parameters=[
            OpenApiParameter("severity", int, OpenApiParameter.QUERY, required=False, enum=HAZARD_SEVERITIES, description="Filter by severity (1=Low, 2=Medium, 3=High)"),
            OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False, enum=HAZARD_STATUSES, description="Filter by status"),
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False, description="Filter by hub ID"),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False, description="Page number"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="Results per page (max 100)"),
        ],
        responses={200: AlertSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = DashboardService()
            qs = service.get_alerts(
                severity=request.query_params.get("severity"),
                status=request.query_params.get("status"),
                hub_id=request.query_params.get("hub_id"),
            )
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = AlertSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardInfrastructureView(APIView):
    permission_classes = [IsAuthenticated, IsDashboardUser]

    @extend_schema(
        tags=["dashboard", "Infrastructure"],
        summary="List infrastructure",
        description="Retrieve paginated list of all infrastructure hubs with live metrics.",
        parameters=[
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False, description="Page number"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="Results per page (max 100)"),
        ],
        responses={200: InfrastructureHubSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = DashboardService()
            qs = service.get_infrastructure()
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = InfrastructureHubSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardInfrastructureDetailView(APIView):
    permission_classes = [IsAuthenticated, IsDashboardUser]

    @extend_schema(
        tags=["dashboard", "Infrastructure"],
        summary="Get infrastructure details",
        description="Retrieve detailed infrastructure data for a specific hub.",
        responses={200: InfrastructureHubSerializer},
    )
    def get(self, request, hub_id):
        try:
            service = DashboardService()
            hub = service.get_infrastructure_hub(hub_id)
            serializer = InfrastructureHubSerializer(hub)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
