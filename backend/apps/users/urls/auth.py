from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from ..views import (
    CustomTokenObtainPairView,
    GoogleLoginView,
    KakaoLoginView,
    LogoutView,
    SignUpView,
)

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # OAuth2 Social Login
    path("google/", GoogleLoginView.as_view(), name="google_login"),
    path("kakao/", KakaoLoginView.as_view(), name="kakao_login"),
]
