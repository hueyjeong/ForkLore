"""
E2E tests for API response format.

These tests verify that:
1. All successful responses are wrapped in {success, message, data, timestamp}
2. Error responses have {success: false, message, errors, timestamp}
3. camelCase is used for JSON keys
"""

import pytest


@pytest.mark.django_db
class TestAPIResponseFormat:
    """All API responses must follow the standard format."""

    def test_success_response_has_standard_wrapper(self, api_client, user):
        """Successful responses have {success, message, data, timestamp}."""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = api_client.get("/api/v1/users/me/")

        assert response.status_code == 200
        data = response.json()

        # Check wrapper structure
        assert data["success"] is True
        assert data["message"] is None
        assert "data" in data
        assert "timestamp" in data

    def test_error_response_has_standard_wrapper(self, api_client):
        """Error responses have {success: false, message, errors, timestamp}."""
        response = api_client.get("/api/v1/users/me/")  # Unauthenticated

        assert response.status_code == 401
        data = response.json()

        assert data["success"] is False
        assert data["message"] is not None
        assert "timestamp" in data

    def test_validation_error_has_field_errors(self, api_client):
        """Validation errors include field-level error details."""
        response = api_client.post(
            "/api/v1/auth/signup/",
            {"email": "invalid"},  # Missing required fields
            format="json",
        )

        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["errors"] is not None

    def test_response_fields_are_camelcase(self, api_client, user):
        """Response JSON keys should be camelCase."""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = api_client.get("/api/v1/users/me/")

        assert response.status_code == 200
        data = response.json()

        # User data should have camelCase keys
        user_data = data["data"]
        assert "profileImageUrl" in user_data or "dateJoined" in user_data

    def test_201_created_response_is_wrapped(self, api_client):
        """POST responses (201 Created) should also be wrapped."""
        response = api_client.post(
            "/api/v1/auth/signup/",
            {
                "email": "newuser@example.com",
                "password": "StrongPass123!",
                "passwordConfirm": "StrongPass123!",
                "nickname": "newuser",
            },
            format="json",
        )

        assert response.status_code == 201
        data = response.json()

        assert data["success"] is True
        assert "timestamp" in data


@pytest.mark.django_db
class TestCamelCaseRequest:
    """API should accept camelCase in request bodies."""

    def test_request_accepts_camelcase(self, authenticated_client):
        """PATCH requests should accept camelCase field names."""
        response = authenticated_client.patch(
            "/api/v1/users/me/",
            {"profileImageUrl": "https://example.com/new.jpg"},
            format="json",
        )

        # Should not error - camelCase should be converted to snake_case
        assert response.status_code == 200
