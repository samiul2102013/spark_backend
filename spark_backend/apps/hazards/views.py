from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.users.permissions import IsAdmin, IsAdminOrCoordinator, IsResidentOrCoordinator
from core.pagination import StandardPagination
from core.responses import created_response, deleted_response, error_response, success_response

from .serializers import CommentSerializer, HazardListSerializer, HazardSerializer
from .services import HazardService


class HazardListView(APIView):

    @extend_schema(
        tags=["mobile"],
        parameters=[
            OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("category", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("period", str, OpenApiParameter.QUERY, required=False),
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

    @extend_schema(tags=["mobile"], request=HazardSerializer, responses={201: HazardSerializer})
    def post(self, request):
        try:
            self.permission_classes = [IsAuthenticated, IsResidentOrCoordinator]
            self.check_permissions(request)
            serializer = HazardSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = HazardService()
            hazard = service.create_hazard(serializer.validated_data, reporter=request.user)
            return created_response(HazardSerializer(hazard).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HazardDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["mobile"], responses={200: HazardSerializer})
    def get(self, request, hazard_id):
        try:
            service = HazardService()
            hazard = service.get_hazard(hazard_id)
            return success_response(HazardSerializer(hazard).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(tags=["mobile"], request=HazardSerializer, responses={200: HazardSerializer})
    def put(self, request, hazard_id):
        try:
            self.permission_classes = [IsAuthenticated, IsAdmin]
            self.check_permissions(request)
            serializer = HazardSerializer(data=request.data, partial=True)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = HazardService()
            hazard = service.update_hazard(hazard_id, serializer.validated_data)
            return success_response(HazardSerializer(hazard).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(tags=["mobile"], responses={204: None})
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

    @extend_schema(tags=["mobile"], responses={200: HazardSerializer})
    def patch(self, request, hazard_id):
        try:
            service = HazardService()
            hazard = service.mark_cleared(hazard_id, request.user)
            return success_response(HazardSerializer(hazard).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HazardCommentListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["mobile"], responses={200: CommentSerializer(many=True)})
    def get(self, request, hazard_id):
        try:
            service = HazardService()
            comments = service.list_comments(hazard_id)
            paginator = StandardPagination()
            page = paginator.paginate_queryset(comments, request)
            serializer = CommentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(tags=["mobile"], request=CommentSerializer, responses={201: CommentSerializer})
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
            return created_response(CommentSerializer(comment).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
