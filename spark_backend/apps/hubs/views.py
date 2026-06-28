from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.bookings.services import BookingService
from apps.users.permissions import IsAdmin, IsAdminOrCoordinator
from core.pagination import StandardPagination
from core.responses import created_response, deleted_response, error_response, success_response

from .serializers import (
    HubAssignResponseSerializer,
    HubAssignSerializer,
    HubCoordinatorSerializer,
    HubListSerializer,
    HubSerializer,
    HubSlotSerializer,
    HubSlotsResponseSerializer,
    HubStatusSerializer,
    NearestHubSerializer,
)
from .services import HubService

HUB_STATUSES = ["open", "closed", "low_battery", "critical"]


class HubListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["mobile", "Hubs"],
        summary="List hubs",
        description="Retrieve a paginated list of all hubs with optional status filter.",
        parameters=[
            OpenApiParameter("status", str, OpenApiParameter.QUERY, required=False, enum=HUB_STATUSES, description="Filter by hub status"),
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False, description="Page number"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="Results per page (max 100)"),
        ],
        responses={200: HubListSerializer(many=True)},
    )
    def get(self, request):
        try:
            service = HubService()
            qs = service.list_hubs(status=request.query_params.get("status"))
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = HubListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        tags=["mobile", "Hubs"],
        summary="Create a hub",
        description="Create a new hub. Admin only.",
        request=HubSerializer,
        responses={201: HubSerializer},
        examples=[
            OpenApiExample(
                "Create Hub Example",
                value={
                    "name": "Kingston Central Hub",
                    "address": "123 Main Street, Kingston",
                    "latitude": 18.1096,
                    "longitude": -77.2975,
                    "status": "open",
                    "max_concurrent_bookings": 5,
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        try:
            self.permission_classes = [IsAuthenticated, IsAdmin]
            self.check_permissions(request)
            serializer = HubSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = HubService()
            hub = service.create_hub(serializer.validated_data)
            return created_response(HubSerializer(hub).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HubDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["mobile", "Hubs"],
        summary="Get hub details",
        description="Retrieve full details of a specific hub by ID.",
        responses={200: HubSerializer},
    )
    def get(self, request, hub_id):
        try:
            service = HubService()
            hub = service.get_hub(hub_id)
            return success_response(HubSerializer(hub).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        tags=["mobile", "Hubs"],
        summary="Update hub",
        description="Partially update a hub's information. Admin only.",
        request=HubSerializer,
        responses={200: HubSerializer},
        examples=[
            OpenApiExample(
                "Update Hub Example",
                value={"status": "low_battery", "battery_percentage": 15},
                request_only=True,
            ),
        ],
    )
    def put(self, request, hub_id):
        try:
            self.permission_classes = [IsAuthenticated, IsAdmin]
            self.check_permissions(request)
            serializer = HubSerializer(data=request.data, partial=True)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = HubService()
            hub = service.update_hub(hub_id, serializer.validated_data)
            return success_response(HubSerializer(hub).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        tags=["mobile", "Hubs"],
        summary="Delete hub",
        description="Delete a hub. Admin only.",
        responses={204: None},
    )
    def delete(self, request, hub_id):
        try:
            self.permission_classes = [IsAuthenticated, IsAdmin]
            self.check_permissions(request)
            service = HubService()
            service.delete_hub(hub_id)
            return deleted_response()
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HubStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrCoordinator]

    @extend_schema(
        tags=["mobile", "Hubs"],
        summary="Update hub status",
        description="Update the operational status and metrics for a hub (battery, solar).",
        request=HubStatusSerializer,
        responses={200: HubSerializer},
        examples=[
            OpenApiExample(
                "Update Hub Status Example",
                value={"status": "low_battery", "battery_percentage": 20, "solar_input_w": 500},
                request_only=True,
            ),
        ],
    )
    def patch(self, request, hub_id):
        try:
            serializer = HubStatusSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            data = serializer.validated_data
            status_val = data.pop("status")
            service = HubService()
            hub = service.update_status(hub_id, status_val, extra=data)
            return success_response(HubSerializer(hub).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HubCoordinatorView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["mobile", "Hubs"],
        summary="Assign coordinator",
        description="Assign a coordinator user to a hub by phone number. Admin only.",
        request=HubCoordinatorSerializer,
        responses={200: HubSerializer},
        examples=[
            OpenApiExample(
                "Assign Coordinator Example",
                value={"coordinator_id": "01856669533"},
                request_only=True,
            ),
        ],
    )
    def patch(self, request, hub_id):
        try:
            serializer = HubCoordinatorSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
            service = HubService()
            hub = service.assign_coordinator(hub_id, serializer.validated_data["coordinator_id"])
            return success_response(HubSerializer(hub).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HubCheckinsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrCoordinator]

    @extend_schema(
        tags=["mobile", "Hubs"],
        summary="List hub check-ins",
        description="Retrieve all check-ins for a specific hub, optionally filtered by date.",
        parameters=[
            OpenApiParameter("date", str, OpenApiParameter.QUERY, required=False, description="Filter by date (YYYY-MM-DD)"),
        ],
        responses={200: dict},
    )
    def get(self, request, hub_id):
        try:
            service = HubService()
            checkins = service.get_hub_checkins(hub_id, date=request.query_params.get("date"))
            from apps.comms.serializers import CheckInSerializer

            serializer = CheckInSerializer(checkins, many=True)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HubBroadcastsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Hubs"],
        summary="List hub broadcasts",
        description="Retrieve all broadcasts for a specific hub.",
        responses={200: dict},
    )
    def get(self, request, hub_id):
        try:
            service = HubService()
            broadcasts = service.get_hub_broadcasts(hub_id)
            from apps.comms.serializers import BroadcastSerializer

            serializer = BroadcastSerializer(broadcasts, many=True)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HubResourcesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Hubs"],
        summary="List hub resources",
        description="Retrieve resource availability for a specific hub.",
        responses={200: dict},
    )
    def get(self, request, hub_id):
        try:
            service = HubService()
            resources = service.get_hub_resources(hub_id)
            return success_response(resources)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HubAssignView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Hubs"],
        summary="Auto-assign nearest hub",
        description="Find the nearest hub to the user's location and assign it to the authenticated user.",
        request=HubAssignSerializer,
        responses={200: HubAssignResponseSerializer},
        examples=[
            OpenApiExample(
                "Assign Hub Example",
                value={"latitude": 18.1096, "longitude": -77.2975},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        try:
            serializer = HubAssignSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)

            lat = float(serializer.validated_data["latitude"])
            lng = float(serializer.validated_data["longitude"])

            service = HubService()
            hub, distance = service.find_nearest_hub(lat, lng)
            if not hub:
                return error_response("No hubs available.", http_status=status.HTTP_404_NOT_FOUND)

            user = request.user
            user.hub = hub
            user.latitude = lat
            user.longitude = lng
            user.save(update_fields=["hub", "latitude", "longitude"])

            hub.distance_km = distance
            return success_response(
                HubAssignResponseSerializer(hub).data,
                message=f"Assigned to nearest hub: {hub.name}",
            )
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NearestHubView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Hubs"],
        summary="Find nearest hub",
        description="Find the nearest hub to the given coordinates using haversine distance calculation.",
        parameters=[
            OpenApiParameter("lat", float, OpenApiParameter.QUERY, required=True, description="User latitude"),
            OpenApiParameter("lng", float, OpenApiParameter.QUERY, required=True, description="User longitude"),
        ],
        responses={200: NearestHubSerializer},
    )
    def get(self, request):
        try:
            lat = request.query_params.get("lat")
            lng = request.query_params.get("lng")
            if not lat or not lng:
                return error_response("lat and lng are required.", http_status=status.HTTP_400_BAD_REQUEST)
            service = HubService()
            hub, distance = service.find_nearest_hub(float(lat), float(lng))
            if not hub:
                return error_response("No hubs available.", http_status=status.HTTP_404_NOT_FOUND)
            hub.distance_km = distance
            return success_response(NearestHubSerializer(hub).data)
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HubSlotsDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["mobile", "Hubs"],
        summary="Hub details with slots",
        description="Get hub details along with 30-min slot availability for a given date.",
        parameters=[
            OpenApiParameter("date", str, OpenApiParameter.QUERY, required=True, description="Date in YYYY-MM-DD format"),
        ],
        responses={200: HubSlotsResponseSerializer},
    )
    def get(self, request, hub_id):
        try:
            date = request.query_params.get("date")
            if not date:
                return error_response("date is required.", http_status=status.HTTP_400_BAD_REQUEST)
            from datetime import datetime
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
            hub_service = HubService()
            hub = hub_service.get_hub(hub_id)
            booking_service = BookingService()
            slots = booking_service.get_hub_slots(hub_id, parsed_date, user=request.user)
            return success_response({
                "hub": HubSerializer(hub).data,
                "slots": slots,
            })
        except Exception as e:
            return error_response(str(e), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
