"""
URL routing for contents app.

Uses nested routing for chapters under branches.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from apps.novels.urls import branches_router

from .views import (
    ChapterDetailViewSet,
    ChapterViewSet,
    MapDetailViewSet,
    MapLayerViewSet,
    MapObjectViewSet,
    MapSnapshotViewSet,
    MapViewSet,
    WikiEntryDetailViewSet,
    WikiEntryViewSet,
    WikiSnapshotViewSet,
    WikiTagDetailViewSet,
    WikiTagViewSet,
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

# Nested router for maps under branches
# /api/v1/branches/{branch_pk}/maps/
maps_router = nested_routers.NestedDefaultRouter(branches_router, r"branches", lookup="branch")
maps_router.register(r"maps", MapViewSet, basename="branch-maps")


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

# Standalone router for map operations by ID
# /api/v1/maps/{pk}/
map_detail_router = DefaultRouter()
map_detail_router.register(r"maps", MapDetailViewSet, basename="maps")

# Nested router for snapshots under wikis
# /api/v1/wikis/{wiki_pk}/snapshots/
snapshots_router = nested_routers.NestedDefaultRouter(wiki_detail_router, r"wikis", lookup="wiki")
snapshots_router.register(r"snapshots", WikiSnapshotViewSet, basename="wiki-snapshots")

# Nested router for map snapshots under maps
# /api/v1/maps/{map_pk}/snapshots/
map_snapshots_router = nested_routers.NestedDefaultRouter(map_detail_router, r"maps", lookup="map")
map_snapshots_router.register(r"snapshots", MapSnapshotViewSet, basename="map-snapshots")

# Standalone router for snapshot operations by ID (for layers)
# /api/v1/snapshots/{pk}/
snapshot_detail_router = DefaultRouter()
snapshot_detail_router.register(r"snapshots", MapSnapshotViewSet, basename="snapshots")

# Nested router for layers under snapshots
# /api/v1/snapshots/{snapshot_pk}/layers/
layers_router = nested_routers.NestedDefaultRouter(
    snapshot_detail_router, r"snapshots", lookup="snapshot"
)
layers_router.register(r"layers", MapLayerViewSet, basename="snapshot-layers")

# Standalone router for layer operations by ID (for objects)
# /api/v1/layers/{pk}/
layer_detail_router = DefaultRouter()
layer_detail_router.register(r"layers", MapLayerViewSet, basename="layers")

# Nested router for objects under layers
# /api/v1/layers/{layer_pk}/objects/
objects_router = nested_routers.NestedDefaultRouter(layer_detail_router, r"layers", lookup="layer")
objects_router.register(r"objects", MapObjectViewSet, basename="layer-objects")


app_name = "contents"

urlpatterns = [
    path("", include(chapters_router.urls)),
    path("", include(chapter_detail_router.urls)),
    path("", include(wikis_router.urls)),
    path("", include(wiki_detail_router.urls)),
    path("", include(wiki_tags_router.urls)),
    path("", include(wiki_tag_detail_router.urls)),
    path("", include(snapshots_router.urls)),
    # Map routes
    path("", include(maps_router.urls)),
    path("", include(map_detail_router.urls)),
    path("", include(map_snapshots_router.urls)),
    path("", include(layers_router.urls)),
    path("", include(layer_detail_router.urls)),
    path("", include(objects_router.urls)),
]
