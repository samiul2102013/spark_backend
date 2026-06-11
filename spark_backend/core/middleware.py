import logging

from django.http import JsonResponse
from rest_framework import status

logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.exception("Unhandled exception", exc_info=exception)
        return JsonResponse(
            {
                "status": "error",
                "data": None,
                "message": "An internal server error occurred.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
