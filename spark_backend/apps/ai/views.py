from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from apps.users.permissions import IsAdmin

from apps.comms.models import CheckIn
from apps.hazards.models import Hazard
from core.pagination import StandardPagination
from core.responses import error_response, success_response

from .models import SituationReport
from .serializers import (
    AIReportingConfigSerializer,
    MessageReviewConfigSerializer,
    MessageReviewItemSerializer,
    MessageReviewStatusUpdateSerializer,
    SituationReportSerializer,
)
from .services import AIConfigService, MessageReviewService, ReportGenerationService


@extend_schema(
    tags=["admin", "AI"],
    summary="Get or update Message Review Config",
    description=(
        "GET: Retrieve the singleton message review configuration. "
        "PUT: Update fields (partial). Returns the full config."
    ),
    request=MessageReviewConfigSerializer,
    responses={200: MessageReviewConfigSerializer},
)
@api_view(["GET", "PUT"])
@permission_classes([IsAdmin])
def message_review_config_view(request):
    if request.method == "GET":
        config = AIConfigService.get_message_review_config()
        return success_response(
            MessageReviewConfigSerializer(config).data
        )

    serializer = MessageReviewConfigSerializer(
        data=request.data, partial=True
    )
    if not serializer.is_valid():
        return error_response(
            serializer.errors, http_status=status.HTTP_400_BAD_REQUEST
        )

    config = AIConfigService.update_message_review_config(
        serializer.validated_data
    )
    return success_response(
        MessageReviewConfigSerializer(config).data
    )


@extend_schema(
    tags=["admin", "AI"],
    summary="Get or update AI Reporting Config",
    description=(
        "GET: Retrieve the singleton AI reporting configuration. "
        "PUT: Update fields (partial). Returns the full config.\n\n"
        "New fields:\n"
        "- structured_reporting: enable extraction/classification/triage sections\n"
        "- include_extraction: include extraction data in AI prompt\n"
        "- include_classification: include classification data in AI prompt\n"
        "- include_triage: include triage/priority data in AI prompt"
    ),
    request=AIReportingConfigSerializer,
    responses={200: AIReportingConfigSerializer},
)
@api_view(["GET", "PUT"])
@permission_classes([IsAdmin])
def ai_reporting_config_view(request):
    if request.method == "GET":
        config = AIConfigService.get_reporting_config()
        return success_response(
            AIReportingConfigSerializer(config).data
        )

    serializer = AIReportingConfigSerializer(
        data=request.data, partial=True
    )
    if not serializer.is_valid():
        return error_response(
            serializer.errors, http_status=status.HTTP_400_BAD_REQUEST
        )

    config = AIConfigService.update_reporting_config(
        serializer.validated_data
    )
    return success_response(
        AIReportingConfigSerializer(config).data
    )


@extend_schema(
    tags=["admin", "AI"],
    summary="List message review queue",
    description=(
        "Paginated list of hazards and check-ins pending review. "
        "Filters: ?status=pending&severity=3&source=hazard"
    ),
    parameters=[
        OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False, enum=["pending", "reviewed", "escalated", "resolved"]),
        OpenApiParameter("severity", int, OpenApiParameter.QUERY, required=False, enum=[1, 2, 3]),
        OpenApiParameter("source", str, OpenApiParameter.QUERY, required=False, enum=["hazard", "checkin"]),
    ],
    responses={200: MessageReviewItemSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAdmin])
def message_review_list_view(request):
    try:
        items = MessageReviewService.get_review_queue(
            status=request.query_params.get("status"),
            severity=request.query_params.get("severity"),
            source=request.query_params.get("source"),
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(items, request)
        serializer = MessageReviewItemSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=["admin", "AI"],
    summary="Get or update a review item",
    description="GET: return single item. PATCH: update review_status, sets reviewed_by and reviewed_at.",
    request=MessageReviewStatusUpdateSerializer,
    responses={200: MessageReviewItemSerializer},
)
@api_view(["GET", "PATCH"])
@permission_classes([IsAdmin])
def message_review_detail_view(request, source, item_id):
    try:
        if request.method == "GET":
            item = MessageReviewService.get_review_item(source, item_id)
            return success_response(MessageReviewItemSerializer(item).data)

        serializer = MessageReviewStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                serializer.errors, http_status=status.HTTP_400_BAD_REQUEST
            )

        item = MessageReviewService.update_review_status(
            source, item_id, serializer.validated_data["review_status"], request.user
        )
        return success_response(MessageReviewItemSerializer(item).data)

    except ValueError as e:
        return error_response(str(e), http_status=status.HTTP_400_BAD_REQUEST)
    except Hazard.DoesNotExist:
        return error_response("Hazard not found", http_status=status.HTTP_404_NOT_FOUND)
    except CheckIn.DoesNotExist:
        return error_response("Check-in not found", http_status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=["admin", "AI"],
    summary="List or create situation reports",
    description=(
        "GET: paginated list of reports (includes extraction, hazard_classification, "
        "triage JSON fields when structured reporting is enabled). "
        "POST: manually trigger a new report."
    ),
    responses={200: SituationReportSerializer(many=True)},
)
@api_view(["GET", "POST"])
@permission_classes([IsAdmin])
def situation_report_list_view(request):
    try:
        if request.method == "GET":
            qs = SituationReport.objects.all()
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = SituationReportSerializer(
                page, many=True, context={"request": request}
            )
            return paginator.get_paginated_response(serializer.data)

        report = ReportGenerationService.create_report(is_auto=False)
        if report is None:
            return error_response(
                "Report could not be generated", http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return success_response(
            SituationReportSerializer(report, context={"request": request}).data,
            http_status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=["admin", "AI"],
    summary="Get or delete a situation report",
    description="GET: single report detail. DELETE: remove a report.",
    responses={200: SituationReportSerializer},
)
@api_view(["GET", "DELETE"])
@permission_classes([IsAdmin])
def situation_report_detail_view(request, report_id):
    try:
        report = SituationReport.objects.get(id=report_id)

        if request.method == "GET":
            return success_response(
                SituationReportSerializer(report, context={"request": request}).data
            )

        report.delete()
        return success_response(None, message="Report deleted", http_status=status.HTTP_204_NO_CONTENT)

    except SituationReport.DoesNotExist:
        return error_response("Report not found", http_status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
