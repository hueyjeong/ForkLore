"""
Views for authentication and user management.
Uses service layer for business logic.
"""

from typing import Any

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from common.pagination import StandardPagination

from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    SignUpSerializer,
    UpdateProfileSerializer,
    UserSerializer,
)
from .services import AuthService

User = get_user_model()


class SignUpView(generics.CreateAPIView):
    """POST /api/v1/auth/signup - Register new user"""

    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "회원가입이 완료되었습니다."},
            status=status.HTTP_201_CREATED,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """POST /api/v1/auth/login - Login and get JWT tokens with user data"""

    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(generics.GenericAPIView):
    """POST /api/v1/auth/logout - Logout by blacklisting refresh token"""

    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            AuthService.logout(refresh_token=serializer.validated_data["refresh"])
            return Response({"message": "로그아웃되었습니다."})
        except ValueError as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/users/me - Get/update current user profile"""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> Any:
        return self.request.user

    def get_serializer_class(self) -> type[serializers.Serializer]:
        if self.request.method in ["PUT", "PATCH"]:
            return UpdateProfileSerializer
        return UserSerializer


class ChangePasswordView(generics.GenericAPIView):
    """POST /api/v1/users/me/password - Change password"""

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"message": "비밀번호가 변경되었습니다."})


class GoogleLoginView(SocialLoginView):
    """POST /api/v1/auth/google/ - Login with Google OAuth2"""

    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000/auth/google/callback"
    client_class = OAuth2Client


class KakaoLoginView(SocialLoginView):
    """POST /api/v1/auth/kakao/ - Login with Kakao OAuth2"""

    adapter_class = KakaoOAuth2Adapter
    callback_url = "http://localhost:3000/auth/kakao/callback"
    client_class = OAuth2Client


class ReadingHistoryView(generics.ListAPIView):
    """GET /api/v1/users/me/reading-history - Get reading history"""

    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    @extend_schema(
        summary="읽은 기록 목록 조회",
        description="내가 최근 읽은 회차 목록을 조회합니다.",
        tags=["Reading"],
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        from apps.interactions.serializers import ReadingLogSerializer
        from apps.interactions.services import ReadingService

        logs = ReadingService.get_recent_reads(user=request.user, limit=100)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(logs, request)
        serializer = ReadingLogSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


class BookmarksView(generics.ListAPIView):
    """GET /api/v1/users/me/bookmarks - Get bookmarks"""

    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    @extend_schema(
        summary="북마크 목록 조회",
        description="내 북마크 목록을 조회합니다.",
        tags=["Reading"],
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        from apps.interactions.serializers import BookmarkSerializer
        from apps.interactions.services import BookmarkService

        bookmarks = BookmarkService.get_bookmarks(user=request.user)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(bookmarks, request)
        serializer = BookmarkSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)
