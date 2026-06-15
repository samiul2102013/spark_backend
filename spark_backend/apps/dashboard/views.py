from drf_spectacular.utils import OpenApiParameter, extend_schema
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


class DashboardOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsDashboardUser]

    @extend_schema(tags=["dashboard"], responses={200: OverviewSerializer})
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
        tags=["dashboard"],
        parameters=[
            OpenApiParameter("lat_min", float, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("lat_max", float, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("lng_min", float, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("lng_max", float, OpenApiParameter.QUERY, required=False),
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
        tags=["dashboard"],
        parameters=[
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False),
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
        tags=["dashboard"],
        parameters=[
            OpenApiParameter("severity", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False),
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

    @extend_schema(tags=["dashboard"], responses={200: InfrastructureHubSerializer(many=True)})
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

    @extend_schema(tags=["dashboard"], responses={200: InfrastructureHubSerializer})
    def get(self, request, hub_id):
        try:
            service = DashboardService()
            hub = service.get_infrastructure_hub(hub_id)
            serializer = InfrastructureHubSerializer(hub)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
