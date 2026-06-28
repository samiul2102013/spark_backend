from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.users.permissions import IsAdmin, IsAdminOrCoordinator, IsResidentOrCoordinator
from core.pagination import StandardPagination
from core.responses import created_response, deleted_response, error_response, success_response

from .serializers import CommentSerializer, HazardListSerializer, HazardSerializer
from .services import HazardService

HAZARD_CATEGORIES = ["flooding", "fallen_tree", "blocked_road", "utility_pole", "medical", "fire", "collapsed_building", "power_line_down", "landslide", "other"]
HAZARD_STATUSES = ["active", "cleared"]
HAZARD_PERIODS = ["pre", "post"]


class HazardListView(APIView):

    @extend_schema(
        tags=["mobile", "Hazards"],
        summary="List hazards",
        description="Retrieve a paginated list of hazards with optional filters.",
        parameters=[
            OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False, enum=HAZARD_STATUSES, description="Filter by status"),
            OpenApiParameter("category", str, OpenApiParameter.QUERY, required=False, enum=HAZARD_CATEGORIES, description="Filter by category"),
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False, description="Filter by hub ID"),
            OpenApiParameter("period", str, OpenApiParameter.QUERY, required=False, enum=HAZARD_PERIODS, description="Filter by disaster period"),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False, description="Page number"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="Results per page (max 100)"),
        ],
        responses={200: HazardListSerializer(many=True)},
    )
    def get(self, request):
        try:
            self.permission_classes = [IsAuthenticated]
            self.check_permissions(request)
            service = HazardService()
            qs = service.list_hazards(
                status=request.query_params.get("status"),
                category=request.query_params.get("category"),
                hub_id=request.query_params.get("hub_id"),
                period=request.query_params.get("period"),
            )
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = HazardListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        tags=["mobile", "Hazards"],
        summary="Create a hazard",
        description="Report a new hazard. The reporter is auto-set to the authenticated user.",
        request=HazardSerializer,
        responses={201: HazardSerializer},
        examples=[
            OpenApiExample(
                "Create Hazard Example",
                value={
                    "category": "flooding",
                    "description": "Water level rising on Main Street",
                    "latitude": 18.1096,
                    "longitude": -77.2975,
                    "severity": 2,
                    "source": "app",
                    "status": "active",
                    "period": "post",
                    "hub": 1,
                    "client_uuid": "uuid-string-here",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        try:
            self.permission_classes = [IsAuthenticated, IsResidentOrCoordinator]
            self.check_permissions(request)
            serializer = HazardSerializer(data=request.data, context={"request": request})
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = HazardService()
            hazard = service.create_hazard(serializer.validated_data, reporter=request.user)
            return created_response(HazardSerializer(hazard, context={"request": request}).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HazardDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Hazards"],
        summary="Get hazard details",
        description="Retrieve full details of a specific hazard by ID.",
        responses={200: HazardSerializer},
    )
    def get(self, request, hazard_id):
        try:
            service = HazardService()
            hazard = service.get_hazard(hazard_id)
            return success_response(HazardSerializer(hazard, context={"request": request}).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        tags=["mobile", "Hazards"],
        summary="Update hazard",
        description="Partially update a hazard. Admin only.",
        request=HazardSerializer,
        responses={200: HazardSerializer},
        examples=[
            OpenApiExample(
                "Update Hazard Example",
                value={"status": "cleared", "severity": 1},
                request_only=True,
            ),
        ],
    )
    def put(self, request, hazard_id):
        try:
            self.permission_classes = [IsAuthenticated, IsAdmin]
            self.check_permissions(request)
            serializer = HazardSerializer(data=request.data, partial=True, context={"request": request})
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = HazardService()
            hazard = service.update_hazard(hazard_id, serializer.validated_data)
            return success_response(HazardSerializer(hazard, context={"request": request}).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        tags=["mobile", "Hazards"],
        summary="Delete hazard",
        description="Delete a hazard. Admin only.",
        responses={204: None},
    )
    def delete(self, request, hazard_id):
        try:
            self.permission_classes = [IsAuthenticated, IsAdmin]
            self.check_permissions(request)
            service = HazardService()
            service.delete_hazard(hazard_id)
            return deleted_response()
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HazardClearView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrCoordinator]

    @extend_schema(
        tags=["mobile", "Hazards"],
        summary="Clear a hazard",
        description="Mark a hazard as cleared by setting status to 'cleared'.",
        responses={200: HazardSerializer},
    )
    def patch(self, request, hazard_id):
        try:
            service = HazardService()
            hazard = service.mark_cleared(hazard_id, request.user)
            return success_response(HazardSerializer(hazard, context={"request": request}).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HazardCommentListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Hazards"],
        summary="List comments",
        description="Retrieve all comments for a specific hazard, paginated.",
        parameters=[
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False, description="Page number"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="Results per page (max 100)"),
        ],
        responses={200: CommentSerializer(many=True)},
    )
    def get(self, request, hazard_id):
        try:
            service = HazardService()
            comments = service.list_comments(hazard_id)
            paginator = StandardPagination()
            page = paginator.paginate_queryset(comments, request)
            serializer = CommentSerializer(page, many=True, context={"request": request})
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        tags=["mobile", "Hazards"],
        summary="Add comment",
        description="Add a comment to a hazard. The hazard is determined by the URL path; do not send `hazard` in the body. The author is auto-set to the authenticated user.",
        request=CommentSerializer,
        responses={201: CommentSerializer},
        examples=[
            OpenApiExample(
                "Add Comment Example (text only)",
                value={"body": "Crew dispatched to investigate"},
                request_only=True,
            ),
            OpenApiExample(
                "Add Comment Example (with photo)",
                value={"body": "Here is an updated photo of the site", "photo": "(upload file)"},
                request_only=True,
            ),
        ],
    )
    def post(self, request, hazard_id):
        try:
            serializer = CommentSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = HazardService()
            comment = service.add_comment(
                hazard_id,
                serializer.validated_data["body"],
                author=request.user,
                photo=serializer.validated_data.get("photo"),
            )
            return created_response(CommentSerializer(comment, context={"request": request}).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
