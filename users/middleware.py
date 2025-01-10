import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse


class ResponseMiddleware(MiddlewareMixin):
    """
    Middleware to intercept all API responses and ensure they follow
    a consistent structure.
    """

    def process_response(self, request, response):
        if request.path.startswith('/swagger') or request.path.startswith('/api/schema'):
            return response
        
        # Bypass non-JSON responses
        if not isinstance(response, JsonResponse):
            try:
                response_data = json.loads(response.content.decode('utf-8'))
            except (ValueError, AttributeError):
                return response

            # Wrap non-JsonResponse objects in JsonResponse
            response = JsonResponse(response_data, status=response.status_code, safe=isinstance(response_data, dict))

        # Modify JsonResponse content to ensure a consistent format
        if isinstance(response, JsonResponse):
            try:
                data = json.loads(response.content.decode('utf-8'))  # Decode content to a Python object
            except json.JSONDecodeError:
                data = None

            if isinstance(data, dict) and {"message", "data", "errors", "status_code"}.issubset(data.keys()):
                return response  # Already formatted, return as is

            # Modify JsonResponse content to ensure a consistent format
            status_code = response.status_code
            response_data = {
                "message": "success" if 200 <= status_code < 300 else "error",
                "data": data if 200 <= status_code < 300 else None,
                "errors": None if 200 <= status_code < 300 else data,
                "status_code": status_code,
            }

            # Update the JsonResponse with the new structure
            response = JsonResponse(response_data, status=status_code)

        return response
