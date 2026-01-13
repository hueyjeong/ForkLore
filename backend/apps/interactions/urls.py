"""
URL routing for interactions app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SubscriptionViewSet, PurchaseViewSet, ChapterPurchaseViewSet


# Main router for subscriptions and purchases
router = DefaultRouter()
router.register(r"subscriptions", SubscriptionViewSet, basename="subscription")
router.register(r"purchases", PurchaseViewSet, basename="purchase")


app_name = "interactions"

urlpatterns = [
    path("", include(router.urls)),
    # Chapter purchase endpoint
    path(
        "chapters/<int:chapter_pk>/purchase/",
        ChapterPurchaseViewSet.as_view({"post": "create"}),
        name="chapter-purchase",
    ),
]
