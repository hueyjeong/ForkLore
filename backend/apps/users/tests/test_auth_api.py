"""
Integration tests for Auth API endpoints.
Tests the full HTTP request/response cycle.
"""

import json
from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.users.models import User


def get_json(response: Response) -> Any:
    """Helper to parse JSON from response content (rendered by StandardJSONRenderer)."""
    return json.loads(response.content)


@pytest.fixture
def api_client() -> APIClient:
    """Return an API client instance."""
    return APIClient()


@pytest.fixture
def user_data() -> dict[str, str]:
    """Valid user registration data."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "passwordConfirm": "TestPassword123!",  # camelCase for API
        "nickname": "testuser",
    }


@pytest.fixture
def existing_user(db: Any) -> User:
    """Create an existing user for tests."""
    user = User.objects.create_user(
        username="existing@example.com",
        email="existing@example.com",
        password="ExistingPassword123!",
        nickname="existinguser",
    )
    return user


# =============================================================================
# Signup Tests
# =============================================================================


class TestSignupEndpoint:
    """Tests for POST /api/v1/auth/signup"""

    def test_signup_success(
        self, api_client: APIClient, db: Any, user_data: dict[str, str]
    ) -> None:
        """Signup with valid data should return 201."""
        url = reverse("signup")
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = get_json(response)
        assert data["success"] is True
        assert "message" in data
        assert User.objects.filter(email=user_data["email"]).exists()

    def test_signup_password_mismatch(
        self, api_client: APIClient, db: Any, user_data: dict[str, str]
    ) -> None:
        """Signup with mismatched passwords should return 400."""
        url = reverse("signup")
        user_data["passwordConfirm"] = "DifferentPassword123!"
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_signup_duplicate_email(
        self, api_client: APIClient, existing_user: User, user_data: dict[str, str]
    ) -> None:
        """Signup with existing email should return 400."""
        url = reverse("signup")
        user_data["email"] = existing_user.email
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_signup_weak_password(
        self, api_client: APIClient, db: Any, user_data: dict[str, str]
    ) -> None:
        """Signup with weak password should return 400."""
        url = reverse("signup")
        user_data["password"] = "weak"
        user_data["passwordConfirm"] = "weak"
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = get_json(response)
        assert "errors" in data
        assert "password" in data["errors"]

    def test_signup_duplicate_nickname(
        self, api_client: APIClient, existing_user: User, user_data: dict[str, str]
    ) -> None:
        """Signup with existing nickname should return 400."""
        url = reverse("signup")
        user_data["nickname"] = existing_user.nickname
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# =============================================================================
# Login Tests
# =============================================================================


class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login"""

    def test_login_success(self, api_client: APIClient, existing_user: User) -> None:
        """Login with valid credentials should return tokens and user data."""
        url = reverse("login")
        response = api_client.post(
            url,
            {"email": existing_user.email, "password": "ExistingPassword123!"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        data = get_json(response)
        assert data["success"] is True
        assert "access" in data["data"]
        assert "refresh" in data["data"]
        assert "user" in data["data"]
        assert data["data"]["user"]["email"] == existing_user.email

    def test_login_invalid_password(self, api_client: APIClient, existing_user: User) -> None:
        """Login with wrong password should return 401."""
        url = reverse("login")
        response = api_client.post(
            url,
            {"email": existing_user.email, "password": "WrongPassword123!"},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client: APIClient, db: Any) -> None:
        """Login with non-existent email should return 401."""
        url = reverse("login")
        response = api_client.post(
            url,
            {"email": "nonexistent@example.com", "password": "SomePassword123!"},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Logout Tests
# =============================================================================


class TestLogoutEndpoint:
    """Tests for POST /api/v1/auth/logout"""

    def test_logout_success(self, api_client: APIClient, existing_user: User) -> None:
        """Logout with valid refresh token should return 200."""
        # First login to get tokens
        login_url = reverse("login")
        login_response = api_client.post(
            login_url,
            {"email": existing_user.email, "password": "ExistingPassword123!"},
            format="json",
        )
        login_data = get_json(login_response)
        access_token = login_data["data"]["access"]
        refresh_token = login_data["data"]["refresh"]

        # Then logout
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        logout_url = reverse("logout")
        response = api_client.post(
            logout_url,
            {"refresh": refresh_token},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        data = get_json(response)
        assert data["success"] is True

    def test_logout_without_auth(self, api_client: APIClient, db: Any) -> None:
        """Logout without authentication should return 401."""
        url = reverse("logout")
        response = api_client.post(url, {"refresh": "some-token"}, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_blacklists_token(self, api_client: APIClient, existing_user: User) -> None:
        """Logout should blacklist the refresh token."""
        # Login to get tokens
        login_url = reverse("login")
        login_response = api_client.post(
            login_url,
            {"email": existing_user.email, "password": "ExistingPassword123!"},
            format="json",
        )
        login_data = get_json(login_response)
        access_token = login_data["data"]["access"]
        refresh_token = login_data["data"]["refresh"]

        # Logout
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        logout_url = reverse("logout")
        api_client.post(logout_url, {"refresh": refresh_token}, format="json")

        # Try to use the same refresh token
        refresh_url = reverse("token_refresh")
        response = api_client.post(
            refresh_url,
            {"refresh": refresh_token},
            format="json",
        )

        # Should be rejected because it's blacklisted
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Token Refresh Tests
# =============================================================================


class TestRefreshEndpoint:
    """Tests for POST /api/v1/auth/refresh"""

    def test_refresh_success(self, api_client: APIClient, existing_user: User) -> None:
        """Refresh with valid token should return new access token."""
        # First login to get tokens
        login_url = reverse("login")
        login_response = api_client.post(
            login_url,
            {"email": existing_user.email, "password": "ExistingPassword123!"},
            format="json",
        )
        login_data = get_json(login_response)
        refresh_token = login_data["data"]["refresh"]

        # Refresh token
        refresh_url = reverse("token_refresh")
        response = api_client.post(
            refresh_url,
            {"refresh": refresh_token},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        data = get_json(response)
        assert "access" in data["data"]

    def test_refresh_invalid_token(self, api_client: APIClient, db: Any) -> None:
        """Refresh with invalid token should return 401."""
        url = reverse("token_refresh")
        response = api_client.post(url, {"refresh": "invalid-token"}, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_expired_token(self, api_client: APIClient, db: Any) -> None:
        """Refresh with expired token should return 401."""
        # Create an intentionally malformed/expired token
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYwOTQ1OTIwMCwianRpIjoiMTIzNDU2Nzg5MCIsInVzZXJfaWQiOjF9.invalid"
        url = reverse("token_refresh")
        response = api_client.post(url, {"refresh": expired_token}, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Me (Profile) Tests
# =============================================================================


class TestMeEndpoint:
    """Tests for GET/PATCH /api/v1/users/me"""

    def test_get_me_success(self, api_client: APIClient, existing_user: User) -> None:
        """Get profile with valid auth should return user data."""
        # Login first
        login_url = reverse("login")
        login_response = api_client.post(
            login_url,
            {"email": existing_user.email, "password": "ExistingPassword123!"},
            format="json",
        )
        login_data = get_json(login_response)
        access_token = login_data["data"]["access"]

        # Get profile
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        me_url = reverse("me")
        response = api_client.get(me_url)

        assert response.status_code == status.HTTP_200_OK
        data = get_json(response)
        assert data["success"] is True
        assert data["data"]["email"] == existing_user.email

    def test_get_me_without_auth(self, api_client: APIClient, db: Any) -> None:
        """Get profile without auth should return 401."""
        url = reverse("me")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_me_success(self, api_client: APIClient, existing_user: User) -> None:
        """Update profile with valid data should return updated user."""
        # Login first
        login_url = reverse("login")
        login_response = api_client.post(
            login_url,
            {"email": existing_user.email, "password": "ExistingPassword123!"},
            format="json",
        )
        login_data = get_json(login_response)
        access_token = login_data["data"]["access"]

        # Update profile
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        me_url = reverse("me")
        response = api_client.patch(
            me_url,
            {"nickname": "newnickname", "bio": "New bio"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        existing_user.refresh_from_db()
        assert existing_user.nickname == "newnickname"
        assert existing_user.bio == "New bio"


# =============================================================================
# Change Password Tests
# =============================================================================


class TestChangePasswordEndpoint:
    """Tests for POST /api/v1/users/me/password"""

    def test_change_password_success(self, api_client: APIClient, existing_user: User) -> None:
        """Change password with valid data should succeed."""
        # Login first
        login_url = reverse("login")
        login_response = api_client.post(
            login_url,
            {"email": existing_user.email, "password": "ExistingPassword123!"},
            format="json",
        )
        login_data = get_json(login_response)
        access_token = login_data["data"]["access"]

        # Change password
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        password_url = reverse("change_password")
        response = api_client.post(
            password_url,
            {"oldPassword": "ExistingPassword123!", "newPassword": "NewPassword456!"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        data = get_json(response)
        assert data["success"] is True

        # Verify new password works
        existing_user.refresh_from_db()
        assert existing_user.check_password("NewPassword456!")

    def test_change_password_wrong_old_password(
        self, api_client: APIClient, existing_user: User
    ) -> None:
        """Change password with wrong old password should fail."""
        # Login first
        login_url = reverse("login")
        login_response = api_client.post(
            login_url,
            {"email": existing_user.email, "password": "ExistingPassword123!"},
            format="json",
        )
        login_data = get_json(login_response)
        access_token = login_data["data"]["access"]

        # Try to change password with wrong old password
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        password_url = reverse("change_password")
        response = api_client.post(
            password_url,
            {"oldPassword": "WrongPassword123!", "newPassword": "NewPassword456!"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
