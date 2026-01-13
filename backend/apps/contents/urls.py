"""
URL routing for contents app.

Uses nested routing for chapters under branches.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from apps.novels.urls import branches_router
from .views import (
    ChapterViewSet,
    ChapterDetailViewSet,
    WikiEntryViewSet,
    WikiEntryDetailViewSet,
    WikiTagViewSet,
    WikiTagDetailViewSet,
    WikiSnapshotViewSet,
)


# Nested router for chapters under branches
# /api/v1/branches/{branch_pk}/chapters/
chapters_router = nested_routers.NestedDefaultRouter(branches_router, r"branches", lookup="branch")
chapters_router.register(r"chapters", ChapterViewSet, basename="branch-chapters")

# Nested router for wikis under branches
# /api/v1/branches/{branch_pk}/wikis/
wikis_router = nested_routers.NestedDefaultRouter(branches_router, r"branches", lookup="branch")
wikis_router.register(r"wikis", WikiEntryViewSet, basename="branch-wikis")

# Nested router for wiki-tags under branches
# /api/v1/branches/{branch_pk}/wiki-tags/
wiki_tags_router = nested_routers.NestedDefaultRouter(branches_router, r"branches", lookup="branch")
wiki_tags_router.register(r"wiki-tags", WikiTagViewSet, basename="branch-wiki-tags")


# Standalone router for chapter operations by ID
# /api/v1/chapters/{pk}/
chapter_detail_router = DefaultRouter()
chapter_detail_router.register(r"chapters", ChapterDetailViewSet, basename="chapters")

# Standalone router for wiki operations by ID
# /api/v1/wikis/{pk}/
wiki_detail_router = DefaultRouter()
wiki_detail_router.register(r"wikis", WikiEntryDetailViewSet, basename="wikis")

# Standalone router for wiki-tag operations by ID
# /api/v1/wiki-tags/{pk}/
wiki_tag_detail_router = DefaultRouter()
wiki_tag_detail_router.register(r"wiki-tags", WikiTagDetailViewSet, basename="wiki-tags")

# Nested router for snapshots under wikis
# /api/v1/wikis/{wiki_pk}/snapshots/
snapshots_router = nested_routers.NestedDefaultRouter(wiki_detail_router, r"wikis", lookup="wiki")
snapshots_router.register(r"snapshots", WikiSnapshotViewSet, basename="wiki-snapshots")


app_name = "contents"

urlpatterns = [
    path("", include(chapters_router.urls)),
    path("", include(chapter_detail_router.urls)),
    path("", include(wikis_router.urls)),
    path("", include(wiki_detail_router.urls)),
    path("", include(wiki_tags_router.urls)),
    path("", include(wiki_tag_detail_router.urls)),
    path("", include(snapshots_router.urls)),
]
