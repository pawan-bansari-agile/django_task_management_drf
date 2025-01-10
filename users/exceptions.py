from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler to ensure a consistent error response.
    """
    # Let DRF handle the exception
    response = exception_handler(exc, context)

    # Customize the response format
    if response is not None:
        response_data = {
            "message": "error",
            "data": None,
            "errors": response.data,
            "status_code": response.status_code,
        }
        return Response(response_data, status=response.status_code)

    # Handle unexpected exceptions
    return Response(
        {
            "message": "error",
            "data": None,
            "errors": {"detail": str(exc)},
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
