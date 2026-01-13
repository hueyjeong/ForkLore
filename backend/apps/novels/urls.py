"""
URL configuration for novels app.

Endpoints:
- /novels/ - Novel CRUD
- /novels/{id}/branches/ - Branch list/create for a novel
- /novels/{id}/branches/main/ - Main branch of a novel
- /branches/{id}/ - Branch detail
- /branches/{id}/visibility/ - Update branch visibility
- /branches/{id}/vote/ - Vote/unvote for a branch
- /branches/{id}/link-request/ - Create link request
- /link-requests/{id}/ - Review link request
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import BranchDetailViewSet, BranchViewSet, LinkRequestViewSet, NovelViewSet

# Main router for novels
router = DefaultRouter()
router.register(r"novels", NovelViewSet, basename="novel")

# Nested router for branches under novels
novels_router = routers.NestedDefaultRouter(router, r"novels", lookup="novel")
novels_router.register(r"branches", BranchViewSet, basename="novel-branches")

# Standalone router for branch details (exported for nested routers)
branches_router = DefaultRouter()
branches_router.register(r"branches", BranchDetailViewSet, basename="branch")

# Standalone router for link requests
link_request_router = DefaultRouter()
link_request_router.register(r"link-requests", LinkRequestViewSet, basename="link-request")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(novels_router.urls)),
    path("", include(branches_router.urls)),
    path("", include(link_request_router.urls)),
]
