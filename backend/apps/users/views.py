"""
Views for authentication and user management.
Uses service layer for business logic.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model

from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from .serializers import (
    SignUpSerializer,
    UserSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
)
from .services import AuthService

User = get_user_model()


class SignUpView(generics.CreateAPIView):
    """POST /api/v1/auth/signup - Register new user"""

    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
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

    def post(self, request):
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

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UpdateProfileSerializer
        return UserSerializer


class ChangePasswordView(generics.GenericAPIView):
    """POST /api/v1/users/me/password - Change password"""

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
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
