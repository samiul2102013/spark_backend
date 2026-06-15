from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import IsAdmin, IsResidentOrCoordinator
from core.responses import created_response, error_response, success_response

from .serializers import BookingSerializer
from .services import BookingService


@extend_schema(
    parameters=[
        OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False),
        OpenApiParameter("hub_id", int, OpenApiParameter.QUERY, required=False),
    ],
    responses={200: BookingSerializer(many=True)},
    tags=["bookings"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def booking_list_view(request):
    user = None if request.user.role == "admin" else request.user
    bookings = BookingService.list_bookings(
        user=user,
        hub_id=request.query_params.get("hub_id"),
        status=request.query_params.get("status"),
    )
    return success_response(BookingSerializer(bookings, many=True).data)


@extend_schema(
    responses={200: BookingSerializer},
    tags=["bookings"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def booking_detail_view(request, booking_id):
    booking = BookingService.get_booking(booking_id)
    return success_response(BookingSerializer(booking).data)


@extend_schema(
    request=BookingSerializer,
    responses={201: BookingSerializer},
    tags=["bookings"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsResidentOrCoordinator])
def booking_create_view(request):
    serializer = BookingSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    booking = BookingService.create_booking(
        user=request.user,
        hub=data["hub"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        client_uuid=data.get("client_uuid"),
    )
    return created_response(BookingSerializer(booking).data)


@extend_schema(
    responses={200: BookingSerializer},
    tags=["bookings"],
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def booking_cancel_view(request, booking_id):
    booking = BookingService.cancel_booking(booking_id)
    return success_response(BookingSerializer(booking).data)


@extend_schema(
    responses={200: BookingSerializer},
    tags=["bookings"],
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsAdmin])
def booking_complete_view(request, booking_id):
    booking = BookingService.complete_booking(booking_id)
    return success_response(BookingSerializer(booking).data)
