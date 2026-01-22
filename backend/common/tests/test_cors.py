"""Tests for CORS configuration."""

import pytest
from django.test import override_settings
from django.test.client import Client
from django.urls import reverse


@pytest.mark.django_db
class TestCORSConfiguration:
    """Test CORS middleware configuration."""

    def test_cors_headers_present_in_development(self):
        """Test that CORS headers are present in development environment."""
        client = Client()

        # Make a request from localhost:3000 (frontend dev server)
        response = client.get(
            reverse("novel-list"),
            HTTP_ORIGIN="http://localhost:3000",
        )

        # Check that CORS headers are present
        assert "Access-Control-Allow-Origin" in response
        assert response["Access-Control-Allow-Origin"] == "http://localhost:3000"

    def test_cors_preflight_request(self):
        """Test CORS preflight OPTIONS request."""
        client = Client()

        response = client.options(
            reverse("novel-list"),
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        )

        # Check that preflight request is handled correctly
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response
        assert "Access-Control-Allow-Methods" in response
        assert "Access-Control-Allow-Headers" in response

    def test_cors_credentials_allowed(self):
        """Test that CORS allows credentials (cookies, authorization headers)."""
        client = Client()

        response = client.get(
            reverse("novel-list"),
            HTTP_ORIGIN="http://localhost:3000",
        )

        # Check that credentials are allowed
        assert "Access-Control-Allow-Credentials" in response
        assert response["Access-Control-Allow-Credentials"] == "true"

    def test_cors_unauthorized_origin_blocked(self):
        """Test that unauthorized origins are blocked."""
        client = Client()

        # Make a request from an unauthorized origin
        response = client.get(
            reverse("novel-list"),
            HTTP_ORIGIN="http://malicious-site.com",
        )

        # Check that CORS headers are NOT present for unauthorized origins
        assert "Access-Control-Allow-Origin" not in response

    @override_settings(
        CORS_ALLOWED_ORIGINS=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )
    def test_multiple_allowed_origins(self):
        """Test that multiple allowed origins are configured correctly."""
        client = Client()

        # Test each allowed origin
        for origin in ["http://localhost:3000", "http://127.0.0.1:3000"]:
            response = client.get(
                reverse("novel-list"),
                HTTP_ORIGIN=origin,
            )
            assert "Access-Control-Allow-Origin" in response
            assert response["Access-Control-Allow-Origin"] == origin

    def test_cors_allowed_methods(self):
        """Test that CORS allows required HTTP methods."""
        client = Client()

        response = client.options(
            reverse("novel-list"),
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        )

        # Check that common methods are allowed
        allowed_methods = response.get("Access-Control-Allow-Methods", "")
        assert "GET" in allowed_methods
        assert "POST" in allowed_methods
        assert "PUT" in allowed_methods
        assert "PATCH" in allowed_methods
        assert "DELETE" in allowed_methods
