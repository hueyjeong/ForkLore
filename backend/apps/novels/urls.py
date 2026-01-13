from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import NovelViewSet

router = DefaultRouter()
router.register(r"", NovelViewSet, basename="novel")

urlpatterns = [
    path("", include(router.urls)),
]
