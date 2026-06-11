from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message="Success", http_status=status.HTTP_200_OK):
    return Response(
        {"status": "success", "data": data, "message": message},
        status=http_status,
    )


def error_response(message="Error", data=None, http_status=status.HTTP_400_BAD_REQUEST):
    return Response(
        {"status": "error", "data": data, "message": message},
        status=http_status,
    )


def created_response(data=None, message="Created successfully"):
    return success_response(data, message, status.HTTP_201_CREATED)


def deleted_response(message="Deleted successfully"):
    return success_response(None, message, status.HTTP_204_NO_CONTENT)
