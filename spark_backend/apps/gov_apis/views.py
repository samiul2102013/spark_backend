from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.hazards.models import Hazard
from core.pagination import StandardPagination
from core.responses import error_response, success_response

from .permissions import GovAPIAccess
from .serializers import (
    GovHazardDetailSerializer,
    GovHazardListSerializer,
    InfrastructureGovSerializer,
    MapDataSerializer,
    OverviewSerializer,
    ReportSerializer,
)
from .services import GovService

class GovOverviewView(APIView):
    permission_classes = [IsAuthenticated, GovAPIAccess]

    @extend_schema(
        tags=["dashboard", "gov"],
        summary="Get government dashboard overview",
        description="Aggregated stats: check-ins, active hubs, hazard reports, silent communications, urgent flags, check-ins over time, hazard breakdown.",
        responses={200: OverviewSerializer},
    )
    def get(self, request):
        try:
            service = GovService()
            data = service.overview()
            return success_response(data)
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GovMapView(APIView):
    permission_classes = [IsAuthenticated, GovAPIAccess]

    @extend_schema(
        tags=["dashboard", "gov"],
        summary="Get map data for government dashboard",
        description="Retrieve map data. Use ?type=hubs|hazards|fallen|medical_needs to return only that section. Omit type to get all.",
        parameters=[
            OpenApiParameter("type", str, OpenApiParameter.QUERY, required=False, enum=["hubs", "hazards", "fallen", "medical_needs"], description="Filter by data type"),
            OpenApiParameter("category", str, OpenApiParameter.QUERY, required=False, description="Filter hazards by category"),
            OpenApiParameter("lat_min", float, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("lat_max", float, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("lng_min", float, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("lng_max", float, OpenApiParameter.QUERY, required=False),
        ],
        responses={200: MapDataSerializer},
    )
    def get(self, request):
        try:
            bounds = {
                "lat_min": request.query_params.get("lat_min"),
                "lat_max": request.query_params.get("lat_max"),
                "lng_min": request.query_params.get("lng_min"),
                "lng_max": request.query_params.get("lng_max"),
            }
            category = request.query_params.get("category")
            data_type = request.query_params.get("type")
            service = GovService()
            data = service.map_data(bounds=bounds, category=category, data_type=data_type)
            return success_response(data)
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


HAZARD_CATEGORIES = [
    "flooding", "fallen_tree", "blocked_road", "utility_pole",
    "medical", "fire", "collapsed_building", "power_line_down",
    "landslide", "other",
]
HAZARD_SEVERITIES = [1, 2, 3]
HAZARD_STATUSES = ["active", "cleared"]


class GovHazardListView(APIView):
    permission_classes = [IsAuthenticated, GovAPIAccess]

    @extend_schema(
        tags=["dashboard", "gov"],
        summary="List hazards",
        description="Retrieve paginated list of all hazards with optional filters for severity, category, and status.",
        parameters=[
            OpenApiParameter("severity", int, OpenApiParameter.QUERY, required=False, enum=HAZARD_SEVERITIES, description="Filter by severity (1=Low, 2=Medium, 3=High)"),
            OpenApiParameter("category", str, OpenApiParameter.QUERY, required=False, enum=HAZARD_CATEGORIES, description="Filter by hazard category"),
            OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False, enum=HAZARD_STATUSES, description="Filter by status"),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False, description="Page number"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="Results per page (max 100)"),
        ],
        responses={200: GovHazardListSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = GovService()
            qs = service.list_hazards(
                severity=request.query_params.get("severity"),
                category=request.query_params.get("category"),
                status=request.query_params.get("status"),
            )
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = GovHazardListSerializer(page, many=True, context={"request": request})
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GovHazardDetailView(APIView):
    permission_classes = [IsAuthenticated, GovAPIAccess]

    @extend_schema(
        tags=["dashboard", "gov"],
        summary="Get hazard detail with comments and images",
        description="Full hazard details including all comments, photos, and metadata.",
        responses={200: GovHazardDetailSerializer},
    )
    def get(self, request, hazard_id):
        try:
            service = GovService()
            hazard = service.hazard_detail(hazard_id)
            serializer = GovHazardDetailSerializer(
                hazard, context={"request": request}
            )
            return success_response(serializer.data)
        except Hazard.DoesNotExist:
            return error_response(
                "Hazard not found", http_status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GovReportsView(APIView):
    permission_classes = [IsAuthenticated, GovAPIAccess]

    @extend_schema(
        tags=["dashboard", "gov"],
        summary="List situation reports (PDFs)",
        description="Retrieve list of situation report PDFs with title, subtitle, timestamp, and download URL.",
        responses={200: ReportSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = GovService()
            data = service.situation_reports()
            return success_response(data)
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GovInfrastructureView(APIView):
    permission_classes = [IsAuthenticated, GovAPIAccess]

    @extend_schema(
        tags=["dashboard", "gov"],
        summary="List all infrastructure hubs",
        description="Paginated list of all hubs with location, status, battery, solar, connectivity, and sync info.",
        parameters=[
            OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False, enum=["online", "offline"], description="Filter by online/offline status"),
        ],
        responses={200: InfrastructureGovSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = GovService()
            qs = service.get_infrastructure(status=request.query_params.get("status"))
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = InfrastructureGovSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GovInfrastructureDetailView(APIView):
    permission_classes = [IsAuthenticated, GovAPIAccess]

    @extend_schema(
        tags=["dashboard", "gov"],
        summary="Get infrastructure hub detail",
        description="Detailed infrastructure data for a single hub.",
        responses={200: InfrastructureGovSerializer},
    )
    def get(self, request, hub_id):
        try:
            service = GovService()
            hub = service.get_infrastructure_hub(hub_id)
            serializer = InfrastructureGovSerializer(hub, context={"request": request})
            return success_response(serializer.data)
        except Hazard.DoesNotExist:
            return error_response(
                "Hub not found", http_status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
