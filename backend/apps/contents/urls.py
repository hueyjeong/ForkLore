"""
URL routing for contents app.

Uses nested routing for chapters under branches.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from apps.novels.urls import branches_router
from .views import ChapterViewSet, ChapterDetailViewSet


# Nested router for chapters under branches
# /api/v1/branches/{branch_pk}/chapters/
chapters_router = nested_routers.NestedDefaultRouter(branches_router, r"branches", lookup="branch")
chapters_router.register(r"chapters", ChapterViewSet, basename="branch-chapters")


# Standalone router for chapter operations by ID
# /api/v1/chapters/{pk}/
chapter_detail_router = DefaultRouter()
chapter_detail_router.register(r"chapters", ChapterDetailViewSet, basename="chapters")


app_name = "contents"

urlpatterns = [
    path("", include(chapters_router.urls)),
    path("", include(chapter_detail_router.urls)),
]
