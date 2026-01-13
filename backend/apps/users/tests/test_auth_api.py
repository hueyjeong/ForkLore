"""
Integration tests for Auth API endpoints.
Tests the full HTTP request/response cycle.
"""

import json

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


def get_json(response):
    """Helper to parse JSON from response content (rendered by StandardJSONRenderer)."""
    return json.loads(response.content)


@pytest.fixture
def api_client():
    """Return an API client instance."""
    return APIClient()


@pytest.fixture
def user_data():
    """Valid user registration data."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "passwordConfirm": "TestPassword123!",  # camelCase for API
        "nickname": "testuser",
    }


@pytest.fixture
def existing_user(db):
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

    def test_signup_success(self, api_client, db, user_data):
        """Signup with valid data should return 201."""
        url = reverse("signup")
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = get_json(response)
        assert data["success"] is True
        assert "message" in data
        assert User.objects.filter(email=user_data["email"]).exists()

    def test_signup_password_mismatch(self, api_client, db, user_data):
        """Signup with mismatched passwords should return 400."""
        url = reverse("signup")
        user_data["passwordConfirm"] = "DifferentPassword123!"
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_signup_duplicate_email(self, api_client, existing_user, user_data):
        """Signup with existing email should return 400."""
        url = reverse("signup")
        user_data["email"] = existing_user.email
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# =============================================================================
# Login Tests
# =============================================================================


class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login"""

    def test_login_success(self, api_client, existing_user):
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

    def test_login_invalid_password(self, api_client, existing_user):
        """Login with wrong password should return 401."""
        url = reverse("login")
        response = api_client.post(
            url,
            {"email": existing_user.email, "password": "WrongPassword123!"},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client, db):
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

    def test_logout_success(self, api_client, existing_user):
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

    def test_logout_without_auth(self, api_client, db):
        """Logout without authentication should return 401."""
        url = reverse("logout")
        response = api_client.post(url, {"refresh": "some-token"}, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Token Refresh Tests
# =============================================================================


class TestRefreshEndpoint:
    """Tests for POST /api/v1/auth/refresh"""

    def test_refresh_success(self, api_client, existing_user):
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

    def test_refresh_invalid_token(self, api_client, db):
        """Refresh with invalid token should return 401."""
        url = reverse("token_refresh")
        response = api_client.post(url, {"refresh": "invalid-token"}, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Me (Profile) Tests
# =============================================================================


class TestMeEndpoint:
    """Tests for GET/PATCH /api/v1/users/me"""

    def test_get_me_success(self, api_client, existing_user):
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

    def test_get_me_without_auth(self, api_client, db):
        """Get profile without auth should return 401."""
        url = reverse("me")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_me_success(self, api_client, existing_user):
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

    def test_change_password_success(self, api_client, existing_user):
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

    def test_change_password_wrong_old_password(self, api_client, existing_user):
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
