from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.users.permissions import IsResidentOrCoordinator
from core.exceptions import BookingConflictError
from core.pagination import StandardPagination
from core.responses import created_response, error_response, success_response

from .serializers import BookingCreateSerializer, BookingSerializer
from .services import BookingService


class BookingListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile"],
        parameters=[
            OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False),
        ],
        responses={200: BookingSerializer(many=True)},
    )
    def get(self, request):
        try:
            user = None if request.user.role == "admin" else request.user
            service = BookingService()
            qs = service.list_bookings(
                user=user,
                hub_id=request.query_params.get("hub_id"),
                status=request.query_params.get("status"),
            )
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = BookingSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        tags=["mobile"], request=BookingCreateSerializer, responses={201: BookingSerializer}
    )
    def post(self, request):
        try:
            self.permission_classes = [IsAuthenticated, IsResidentOrCoordinator]
            self.check_permissions(request)
            serializer = BookingCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = BookingService()
            booking = service.create_booking(request.user, serializer.validated_data)
            return created_response(BookingSerializer(booking).data)
        except BookingConflictError as e:
            return error_response(str(e), http_status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["mobile"], responses={200: BookingSerializer})
    def get(self, request, booking_id):
        try:
            service = BookingService()
            booking = service.get_booking(booking_id)
            return success_response(BookingSerializer(booking).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookingCancelView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["mobile"], responses={200: BookingSerializer})
    def patch(self, request, booking_id):
        try:
            service = BookingService()
            booking = service.cancel_booking(booking_id, request.user)
            return success_response(BookingSerializer(booking).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HubSlotsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile"],
        parameters=[
            OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=True),
            OpenApiParameter("date", str, OpenApiParameter.QUERY, required=True),
        ],
        responses={200: dict},
    )
    def get(self, request):
        try:
            hub_id = request.query_params.get("hub_id")
            date = request.query_params.get("date")
            if not hub_id or not date:
                return error_response(
                    "hub_id and date are required.", http_status=status.HTTP_400_BAD_REQUEST
                )
            from datetime import datetime

            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
            service = BookingService()
            slots = service.get_available_slots(hub_id, parsed_date)
            return success_response(slots)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
