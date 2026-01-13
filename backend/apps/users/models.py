from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    READER = "READER", "Reader"
    AUTHOR = "AUTHOR", "Author"
    ADMIN = "ADMIN", "Admin"


class AuthProvider(models.TextChoices):
    LOCAL = "LOCAL", "Local"
    GOOGLE = "GOOGLE", "Google"
    KAKAO = "KAKAO", "Kakao"


class User(AbstractUser):
    email = models.EmailField("이메일", unique=True)
    nickname = models.CharField("닉네임", max_length=50, unique=True)
    profile_image_url = models.URLField("프로필 이미지", blank=True)
    bio = models.TextField("소개", blank=True)
    birth_date = models.DateField("생년월일", null=True, blank=True)

    role = models.CharField(
        "역할", max_length=20, choices=UserRole.choices, default=UserRole.READER
    )
    auth_provider = models.CharField(
        "인증 제공자", max_length=20, choices=AuthProvider.choices, default=AuthProvider.LOCAL
    )
    provider_id = models.CharField("제공자 ID", max_length=255, blank=True)

    mileage = models.IntegerField("마일리지", default=0)
    coin = models.IntegerField("코인", default=0)
    email_verified = models.BooleanField("이메일 인증 여부", default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "nickname"]

    class Meta:
        db_table = "users"
        verbose_name = "사용자"
        verbose_name_plural = "사용자들"

    def __str__(self) -> str:
        return self.nickname

    @property
    def is_author(self) -> bool:
        return self.role in [UserRole.AUTHOR, UserRole.ADMIN]
