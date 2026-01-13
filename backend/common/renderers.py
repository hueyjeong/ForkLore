"""
Standard JSON Renderer with response wrapper and camelCase support.

This renderer:
1. Wraps all successful responses (status < 400) in a standard format
2. Converts snake_case keys to camelCase for JSON output
3. Error responses are NOT wrapped here - they are handled by custom_exception_handler

Standard Response Format:
{
    "success": true,
    "message": null,
    "data": <original_data>,
    "timestamp": "2026-01-13T12:00:00+09:00"
}
"""

from typing import Any

from django.utils import timezone
from djangorestframework_camel_case.render import CamelCaseJSONRenderer


class StandardJSONRenderer(CamelCaseJSONRenderer):
    """
    Custom JSON renderer that:
    1. Wraps all success responses in standard format
    2. Applies camelCase transformation to keys

    Error responses (4xx, 5xx) pass through unchanged - they are
    handled by custom_exception_handler in common/exceptions.py.
    """

    def render(
        self,
        data: Any,
        accepted_media_type: str | None = None,
        renderer_context: dict[str, Any] | None = None,
    ) -> Any:
        # Handle missing context
        if renderer_context is None:
            return super().render(data, accepted_media_type, renderer_context)

        response = renderer_context.get("response")

        # Skip wrapping if already wrapped (has 'success' key)
        if isinstance(data, dict) and "success" in data:
            return super().render(data, accepted_media_type, renderer_context)

        # Only wrap success responses (status < 400)
        if response and response.status_code < 400:
            data = {
                "success": True,
                "message": None,
                "data": data,
                "timestamp": timezone.now().isoformat(),
            }

        return super().render(data, accepted_media_type, renderer_context)
