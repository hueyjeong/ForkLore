"""
Custom renderers for standardized API responses.
"""

from datetime import datetime, timezone

from rest_framework.renderers import JSONRenderer


class StandardJSONRenderer(JSONRenderer):
    """
    Custom JSON renderer that wraps all responses in a standard format.

    Success response format:
    {
        "success": true,
        "message": "Operation completed",
        "data": { ... },
        "timestamp": "2026-01-13T14:55:00.000Z"
    }

    Error responses are handled by the exception handler and passed through as-is.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None

        # Don't wrap error responses (they're handled by exception handler)
        if response and response.status_code >= 400:
            # Check if this is already a wrapped error response from exception handler
            if isinstance(data, dict) and "success" in data and data.get("success") is False:
                return super().render(data, accepted_media_type, renderer_context)
            # Otherwise, wrap the error
            wrapped = {
                "success": False,
                "message": self._extract_error_message(data),
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
            return super().render(wrapped, accepted_media_type, renderer_context)

        # Wrap success responses
        wrapped = {
            "success": True,
            "message": self._extract_success_message(data, response),
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

        return super().render(wrapped, accepted_media_type, renderer_context)

    def _extract_success_message(self, data, response):
        """Extract or generate a success message."""
        if isinstance(data, dict) and "message" in data:
            msg = data.pop("message")
            return msg
        if response:
            if response.status_code == 201:
                return "Created successfully"
            elif response.status_code == 204:
                return "Deleted successfully"
        return "Request completed successfully"

    def _extract_error_message(self, data):
        """Extract or generate an error message from error data."""
        if isinstance(data, dict):
            if "detail" in data:
                return str(data["detail"])
            if "message" in data:
                return str(data["message"])
            # For validation errors, return first error
            for key, value in data.items():
                if isinstance(value, list) and value:
                    return f"{key}: {value[0]}"
                elif isinstance(value, str):
                    return f"{key}: {value}"
        elif isinstance(data, str):
            return data
        return "An error occurred"
