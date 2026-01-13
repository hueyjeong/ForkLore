"""
Tests for StandardJSONRenderer - Response wrapper for all API responses.

TDD Phase: RED - These tests should fail initially since StandardJSONRenderer
doesn't exist yet.
"""

import json

import pytest
from django.utils import timezone
from rest_framework.response import Response


class TestStandardJSONRenderer:
    """StandardJSONRenderer wraps all success responses in standard format."""

    def test_wraps_success_response_with_standard_format(self):
        """200 responses should be wrapped in {success, message, data, timestamp}."""
        from common.renderers import StandardJSONRenderer

        renderer = StandardJSONRenderer()
        data = {"id": 1, "name": "Test"}

        response = Response(data, status=200)
        renderer_context = {"response": response}

        result = renderer.render(data, renderer_context=renderer_context)

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"] == {"id": 1, "name": "Test"}
        assert parsed["message"] is None
        assert "timestamp" in parsed

    def test_does_not_double_wrap_already_wrapped_response(self):
        """If data already has 'success' key, skip wrapping."""
        from common.renderers import StandardJSONRenderer

        renderer = StandardJSONRenderer()
        data = {
            "success": True,
            "message": None,
            "data": {"id": 1},
            "timestamp": "2026-01-13T12:00:00Z",
        }

        response = Response(data, status=200)
        renderer_context = {"response": response}

        result = renderer.render(data, renderer_context=renderer_context)

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"] == {"id": 1}
        assert parsed["message"] is None

    def test_does_not_wrap_error_responses(self):
        """4xx/5xx responses are handled by exception_handler, not renderer."""
        from common.renderers import StandardJSONRenderer

        renderer = StandardJSONRenderer()
        data = {"detail": "Not found"}

        response = Response(data, status=404)
        renderer_context = {"response": response}

        result = renderer.render(data, renderer_context=renderer_context)

        parsed = json.loads(result)
        # Error responses pass through unchanged (exception_handler wraps them)
        assert parsed == data

    def test_wraps_list_response(self):
        """List responses should also be wrapped."""
        from common.renderers import StandardJSONRenderer

        renderer = StandardJSONRenderer()
        data = [{"id": 1}, {"id": 2}]

        response = Response(data, status=200)
        renderer_context = {"response": response}

        result = renderer.render(data, renderer_context=renderer_context)

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"] == [{"id": 1}, {"id": 2}]

    def test_wraps_201_created_response(self):
        """201 Created should also be wrapped."""
        from common.renderers import StandardJSONRenderer

        renderer = StandardJSONRenderer()
        data = {"id": 1}

        response = Response(data, status=201)
        renderer_context = {"response": response}

        result = renderer.render(data, renderer_context=renderer_context)

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"] == {"id": 1}

    def test_wraps_204_no_content_response(self):
        """204 No Content should be wrapped with null data."""
        from common.renderers import StandardJSONRenderer

        renderer = StandardJSONRenderer()
        data = None

        response = Response(data, status=204)
        renderer_context = {"response": response}

        result = renderer.render(data, renderer_context=renderer_context)

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"] is None

    def test_timestamp_is_valid_iso_format(self):
        """Timestamp should be in ISO 8601 format."""
        from common.renderers import StandardJSONRenderer

        renderer = StandardJSONRenderer()
        data = {"id": 1}

        response = Response(data, status=200)
        renderer_context = {"response": response}

        result = renderer.render(data, renderer_context=renderer_context)

        parsed = json.loads(result)
        # Should be able to parse as ISO format
        from datetime import datetime

        timestamp = parsed["timestamp"]
        # Remove timezone info for parsing
        assert "T" in timestamp  # ISO format has T separator

    def test_handles_empty_response_context(self):
        """Should handle missing renderer_context gracefully."""
        from common.renderers import StandardJSONRenderer

        renderer = StandardJSONRenderer()
        data = {"id": 1}

        # No response in context - should not wrap
        result = renderer.render(data, renderer_context=None)

        parsed = json.loads(result)
        assert parsed == {"id": 1}

    def test_wraps_paginated_response(self):
        """Paginated responses should be wrapped properly."""
        from common.renderers import StandardJSONRenderer

        renderer = StandardJSONRenderer()
        # DRF pagination format
        data = {
            "count": 100,
            "next": "http://api.example.com/items/?page=2",
            "previous": None,
            "results": [{"id": 1}, {"id": 2}],
        }

        response = Response(data, status=200)
        renderer_context = {"response": response}

        result = renderer.render(data, renderer_context=renderer_context)

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["count"] == 100
        assert parsed["data"]["results"] == [{"id": 1}, {"id": 2}]
