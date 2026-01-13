"""
Service layer for authentication and user management.
Implements business logic separate from views/serializers.
"""

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()


class AuthService:
    """Service class for authentication operations."""

    @staticmethod
    def signup(
        email: str,
        password: str,
        password_confirm: str,
        nickname: str,
        birth_date: str | None = None,
    ) -> User:
        """
        Register a new user.

        Args:
            email: User's email address (used as username)
            password: User's password
            password_confirm: Password confirmation
            nickname: User's display name
            birth_date: Optional birth date (YYYY-MM-DD)

        Returns:
            Created User instance

        Raises:
            ValueError: If validation fails
        """
        # Validate password match
        if password != password_confirm:
            raise ValueError("비밀번호가 일치하지 않습니다.")

        # Check email uniqueness
        if User.objects.filter(email=email).exists():
            raise ValueError("이미 사용 중인 이메일입니다.")

        # Check nickname uniqueness
        if User.objects.filter(nickname=nickname).exists():
            raise ValueError("이미 사용 중인 닉네임입니다.")

        # Create user
        user = User(
            username=email,
            email=email,
            nickname=nickname,
        )
        if birth_date:
            user.birth_date = birth_date

        user.set_password(password)
        user.save()

        return user

    @staticmethod
    def login(email: str, password: str) -> dict:
        """
        Authenticate user and return JWT tokens.

        Args:
            email: User's email address
            password: User's password

        Returns:
            Dictionary containing access token, refresh token, and user data

        Raises:
            ValueError: If credentials are invalid
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")

        if not user.check_password(password):
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "role": user.role,
            },
        }

    @staticmethod
    def logout(refresh_token: str) -> bool:
        """
        Blacklist the refresh token to log out user.

        Args:
            refresh_token: The refresh token to blacklist

        Returns:
            True if successful

        Raises:
            ValueError: If token is invalid
        """
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return True
        except TokenError:
            raise ValueError("유효하지 않은 토큰입니다.")

    @staticmethod
    def refresh(refresh_token: str) -> dict:
        """
        Refresh the access token using a valid refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            Dictionary containing new access token (and optionally new refresh token)

        Raises:
            ValueError: If token is invalid
        """
        try:
            token = RefreshToken(refresh_token)
            return {
                "access": str(token.access_token),
            }
        except TokenError:
            raise ValueError("유효하지 않은 토큰입니다.")


class UserService:
    """Service class for user profile operations."""

    @staticmethod
    def get_profile(user: User) -> dict:
        """
        Get user profile data.

        Args:
            user: The User instance

        Returns:
            Dictionary containing user profile data
        """
        return {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "profile_image_url": user.profile_image_url,
            "bio": user.bio,
            "birth_date": str(user.birth_date) if user.birth_date else None,
            "role": user.role,
            "mileage": user.mileage,
            "coin": user.coin,
            "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        }

    @staticmethod
    def update_profile(
        user: User,
        nickname: str | None = None,
        profile_image_url: str | None = None,
        bio: str | None = None,
        birth_date: str | None = None,
    ) -> User:
        """
        Update user profile fields.

        Args:
            user: The User instance to update
            nickname: New nickname (optional)
            profile_image_url: New profile image URL (optional)
            bio: New bio text (optional)
            birth_date: New birth date (optional)

        Returns:
            Updated User instance

        Raises:
            ValueError: If validation fails
        """
        # Check nickname uniqueness if changing
        if nickname and nickname != user.nickname:
            if User.objects.filter(nickname=nickname).exists():
                raise ValueError("이미 사용 중인 닉네임입니다.")
            user.nickname = nickname

        if profile_image_url is not None:
            user.profile_image_url = profile_image_url

        if bio is not None:
            user.bio = bio

        if birth_date is not None:
            user.birth_date = birth_date

        user.save()
        return user

    @staticmethod
    def change_password(user: User, old_password: str, new_password: str) -> bool:
        """
        Change user's password.

        Args:
            user: The User instance
            old_password: Current password
            new_password: New password

        Returns:
            True if successful

        Raises:
            ValueError: If old password is incorrect
        """
        if not user.check_password(old_password):
            raise ValueError("기존 비밀번호가 올바르지 않습니다.")

        user.set_password(new_password)
        user.save()
        return True
