from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.users.permissions import IsDashboardUser
from core.pagination import StandardPagination
from core.responses import error_response, success_response

from .serializers import UrgentFlagSerializer
from .services import ALL_CATEGORIES, DashboardService


class UrgentFlagsView(APIView):
    permission_classes = [IsAuthenticated, IsDashboardUser]

    @extend_schema(
        tags=["dashboard", "Urgent Flags"],
        summary="Dashboard overview — hazard breakdown, check-ins & hazard list",
        description=(
            "Returns a hazard breakdown by all categories, check-in statistics, "
            "and a paginated list of hazards with optional filters."
        ),
        parameters=[
            OpenApiParameter(
                "category",
                str,
                OpenApiParameter.QUERY,
                required=False,
                enum=ALL_CATEGORIES,
            ),
            OpenApiParameter(
                "status",
                str,
                OpenApiParameter.QUERY,
                required=False,
                enum=["active", "cleared"],
            ),
            OpenApiParameter(
                "period",
                str,
                OpenApiParameter.QUERY,
                required=False,
                enum=["pre", "post"],
            ),
            OpenApiParameter("severity", int, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("hours", int, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False),
        ],
        responses={200: UrgentFlagSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = DashboardService()

            hazard_breakdown, checkins = service.overview()

            qs = service.list_urgent_flags(
                category=request.query_params.get("category"),
                status=request.query_params.get("status"),
                period=request.query_params.get("period"),
                severity=request.query_params.get("severity"),
                hours=request.query_params.get("hours"),
            )

            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = UrgentFlagSerializer(page, many=True, context={"request": request})

            data = {
                "hazard_breakdown": hazard_breakdown,
                "checkins": checkins,
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": serializer.data,
            }
            return success_response(data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#hi i am samiul