from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


class SparkBaseError(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An unexpected error occurred."
    default_code = "internal_error"

    def __init__(self, detail=None, code=None):
        self.detail = detail or self.default_detail
        self.code = code or self.default_code
        super().__init__(self.detail)


class HubFullError(SparkBaseError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Hub is at full capacity."
    default_code = "hub_full"


class BookingConflictError(SparkBaseError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Slot already booked."
    default_code = "booking_conflict"


class OfflineConflictError(SparkBaseError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Server data is newer. Conflict logged."
    default_code = "sync_conflict"


class HubNotFoundError(SparkBaseError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Hub not found."
    default_code = "hub_not_found"


def custom_exception_handler(exc, context):
    if isinstance(exc, SparkBaseError):
        return Response(
            {
                "status": "error",
                "data": None,
                "message": exc.detail,
                "code": exc.code,
            },
            status=exc.status_code,
        )
    return exception_handler(exc, context)
