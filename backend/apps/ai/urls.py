"""
URL configuration for AI app.

AI endpoints are nested under branches:
- /branches/{id}/ai/wiki-suggestions
- /branches/{id}/ai/consistency-check
- /branches/{id}/ai/ask
- /branches/{id}/ai/create-chunks
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from apps.novels.urls import branches_router
from .views import AIViewSet


# Nested router for AI under branches
branches_ai_router = routers.NestedDefaultRouter(branches_router, r"branches", lookup="branch")
branches_ai_router.register(r"ai", AIViewSet, basename="branch-ai")

urlpatterns = [
    path("", include(branches_ai_router.urls)),
]
