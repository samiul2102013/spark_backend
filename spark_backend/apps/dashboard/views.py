from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.responses import success_response

from .services import DashboardService


@extend_schema(
    responses={200: dict},
    tags=["dashboard"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_overview_view(request):
    data = DashboardService.overview()
    return success_response(data)


@extend_schema(
    responses={200: dict},
    tags=["dashboard"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_map_view(request):
    data = DashboardService.map_data()
    return success_response(data)


@extend_schema(
    parameters=[
        OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False),
    ],
    responses={200: dict},
    tags=["dashboard"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_reports_view(request):
    reports = DashboardService.situation_reports(hub_id=request.query_params.get("hub_id"))
    return success_response(
        [
            {
                "id": r.id,
                "hub": r.hub_id,
                "summary": r.summary,
                "generated_by": r.generated_by,
                "is_auto": r.is_auto,
                "created_at": r.created_at.isoformat(),
            }
            for r in reports
        ]
    )
