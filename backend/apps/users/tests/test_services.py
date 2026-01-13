"""
Unit tests for AuthService and UserService.
Following TDD: Write tests first, then implement.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.services import AuthService, UserService

User = get_user_model()


@pytest.fixture
def user_data():
    """Valid user registration data."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "password_confirm": "TestPassword123!",
        "nickname": "testuser",
        "birth_date": "1990-01-01",
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
# AuthService Tests
# =============================================================================


class TestAuthServiceSignup:
    """Tests for AuthService.signup()"""

    def test_signup_creates_user(self, db, user_data):
        """signup() should create a new user with valid data."""
        user = AuthService.signup(
            email=user_data["email"],
            password=user_data["password"],
            password_confirm=user_data["password_confirm"],
            nickname=user_data["nickname"],
            birth_date=user_data["birth_date"],
        )

        assert user is not None
        assert user.email == user_data["email"]
        assert user.nickname == user_data["nickname"]
        assert user.check_password(user_data["password"])
        assert user.username == user_data["email"]  # username = email

    def test_signup_password_mismatch_raises_error(self, db, user_data):
        """signup() should raise ValueError if passwords don't match."""
        with pytest.raises(ValueError, match="비밀번호가 일치하지 않습니다"):
            AuthService.signup(
                email=user_data["email"],
                password=user_data["password"],
                password_confirm="DifferentPassword123!",
                nickname=user_data["nickname"],
            )

    def test_signup_duplicate_email_raises_error(self, existing_user, user_data):
        """signup() should raise ValueError if email already exists."""
        with pytest.raises(ValueError, match="이미 사용 중인 이메일"):
            AuthService.signup(
                email=existing_user.email,
                password=user_data["password"],
                password_confirm=user_data["password_confirm"],
                nickname="differentnick",
            )

    def test_signup_duplicate_nickname_raises_error(self, existing_user, user_data):
        """signup() should raise ValueError if nickname already exists."""
        with pytest.raises(ValueError, match="이미 사용 중인 닉네임"):
            AuthService.signup(
                email=user_data["email"],
                password=user_data["password"],
                password_confirm=user_data["password_confirm"],
                nickname=existing_user.nickname,
            )


class TestAuthServiceLogin:
    """Tests for AuthService.login()"""

    def test_login_returns_tokens(self, existing_user):
        """login() should return access and refresh tokens."""
        result = AuthService.login(
            email=existing_user.email,
            password="ExistingPassword123!",
        )

        assert "access" in result
        assert "refresh" in result
        assert "user" in result
        assert result["user"]["email"] == existing_user.email

    def test_login_invalid_email_raises_error(self, db):
        """login() should raise ValueError for non-existent email."""
        with pytest.raises(ValueError, match="이메일 또는 비밀번호가 올바르지 않습니다"):
            AuthService.login(
                email="nonexistent@example.com",
                password="SomePassword123!",
            )

    def test_login_invalid_password_raises_error(self, existing_user):
        """login() should raise ValueError for wrong password."""
        with pytest.raises(ValueError, match="이메일 또는 비밀번호가 올바르지 않습니다"):
            AuthService.login(
                email=existing_user.email,
                password="WrongPassword123!",
            )


class TestAuthServiceLogout:
    """Tests for AuthService.logout()"""

    def test_logout_blacklists_refresh_token(self, existing_user):
        """logout() should blacklist the refresh token."""
        refresh = RefreshToken.for_user(existing_user)
        refresh_token = str(refresh)

        result = AuthService.logout(refresh_token=refresh_token)

        assert result is True

    def test_logout_invalid_token_raises_error(self, db):
        """logout() should raise ValueError for invalid token."""
        with pytest.raises(ValueError, match="유효하지 않은 토큰"):
            AuthService.logout(refresh_token="invalid-token")


class TestAuthServiceRefresh:
    """Tests for AuthService.refresh()"""

    def test_refresh_returns_new_tokens(self, existing_user):
        """refresh() should return new access token."""
        refresh = RefreshToken.for_user(existing_user)
        refresh_token = str(refresh)

        result = AuthService.refresh(refresh_token=refresh_token)

        assert "access" in result
        assert result["access"] != str(refresh.access_token)

    def test_refresh_invalid_token_raises_error(self, db):
        """refresh() should raise ValueError for invalid token."""
        with pytest.raises(ValueError, match="유효하지 않은 토큰"):
            AuthService.refresh(refresh_token="invalid-token")


# =============================================================================
# UserService Tests
# =============================================================================


class TestUserServiceGetProfile:
    """Tests for UserService.get_profile()"""

    def test_get_profile_returns_user_data(self, existing_user):
        """get_profile() should return user profile data."""
        profile = UserService.get_profile(user=existing_user)

        assert profile["id"] == existing_user.id
        assert profile["email"] == existing_user.email
        assert profile["nickname"] == existing_user.nickname
        assert "role" in profile


class TestUserServiceUpdateProfile:
    """Tests for UserService.update_profile()"""

    def test_update_profile_changes_fields(self, existing_user):
        """update_profile() should update allowed fields."""
        updated_user = UserService.update_profile(
            user=existing_user,
            nickname="newnickname",
            bio="New bio text",
        )

        assert updated_user.nickname == "newnickname"
        assert updated_user.bio == "New bio text"

    def test_update_profile_duplicate_nickname_raises_error(self, existing_user, db):
        """update_profile() should raise ValueError for duplicate nickname."""
        # Create another user
        User.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="OtherPassword123!",
            nickname="othernick",
        )

        with pytest.raises(ValueError, match="이미 사용 중인 닉네임"):
            UserService.update_profile(
                user=existing_user,
                nickname="othernick",  # Try to use other user's nickname
            )


class TestUserServiceChangePassword:
    """Tests for UserService.change_password()"""

    def test_change_password_updates_password(self, existing_user):
        """change_password() should update the user's password."""
        result = UserService.change_password(
            user=existing_user,
            old_password="ExistingPassword123!",
            new_password="NewPassword456!",
        )

        assert result is True
        existing_user.refresh_from_db()
        assert existing_user.check_password("NewPassword456!")

    def test_change_password_wrong_old_password_raises_error(self, existing_user):
        """change_password() should raise ValueError for wrong old password."""
        with pytest.raises(ValueError, match="기존 비밀번호가 올바르지 않습니다"):
            UserService.change_password(
                user=existing_user,
                old_password="WrongPassword123!",
                new_password="NewPassword456!",
            )
