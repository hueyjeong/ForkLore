"""
URL routing for interactions app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SubscriptionViewSet,
    PurchaseViewSet,
    ChapterPurchaseViewSet,
    ChapterCommentViewSet,
    CommentDetailViewSet,
    ChapterLikeViewSet,
    ReportViewSet,
    AdminReportViewSet,
)


# Main router for subscriptions and purchases
router = DefaultRouter()
router.register(r"subscriptions", SubscriptionViewSet, basename="subscription")
router.register(r"purchases", PurchaseViewSet, basename="purchase")
router.register(r"comments", CommentDetailViewSet, basename="comment")
router.register(r"reports", ReportViewSet, basename="report")

# Admin router
admin_router = DefaultRouter()
admin_router.register(r"reports", AdminReportViewSet, basename="admin-report")


app_name = "interactions"

urlpatterns = [
    path("", include(router.urls)),
    # Admin routes
    path("admin/", include(admin_router.urls)),
    # Chapter purchase endpoint
    path(
        "chapters/<int:chapter_pk>/purchase/",
        ChapterPurchaseViewSet.as_view({"post": "create"}),
        name="chapter-purchase",
    ),
    # Chapter comments endpoint
    path(
        "chapters/<int:chapter_pk>/comments/",
        ChapterCommentViewSet.as_view({"get": "list", "post": "create"}),
        name="chapter-comments",
    ),
    # Chapter like endpoint
    path(
        "chapters/<int:chapter_pk>/like/",
        ChapterLikeViewSet.as_view({"post": "create", "delete": "create"}),
        name="chapter-like",
    ),
]
