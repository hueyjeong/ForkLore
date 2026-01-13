"""
ViewSet Tests for Subscription/Purchase API endpoints.

Tests:
- POST /subscriptions/ - Subscribe
- DELETE /subscriptions/current/ - Cancel subscription
- GET /subscriptions/status/ - Get subscription status
- GET /purchases/ - List purchases
- POST /chapters/{id}/purchase/ - Purchase chapter
"""

from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.contents.models import AccessType, Chapter, ChapterStatus
from apps.interactions.models import PlanType, Purchase, Subscription, SubscriptionStatus
from apps.users.models import User


def get_tokens_for_user(user):
    """Generate JWT tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


@pytest.mark.django_db
class TestSubscriptionCreate:
    """Tests for POST /subscriptions/"""

    def test_create_subscription(self):
        """Should create a new subscription."""
        user = baker.make(User)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        url = "/api/v1/subscriptions/"
        data = {"planType": "BASIC", "days": 30}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert resp_data["success"] is True
        assert resp_data["data"]["planType"] == "BASIC"

    def test_create_subscription_unauthenticated(self):
        """Should reject unauthenticated request."""
        client = APIClient()

        url = "/api/v1/subscriptions/"
        data = {"planType": "BASIC", "days": 30}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestSubscriptionCancel:
    """Tests for DELETE /subscriptions/current/"""

    def test_cancel_subscription(self):
        """Should cancel active subscription."""
        user = baker.make(User)
        baker.make(
            Subscription,
            user=user,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
        )
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        url = "/api/v1/subscriptions/current/"
        response = client.delete(url)

        assert response.status_code == status.HTTP_200_OK

    def test_cancel_no_subscription(self):
        """Should return 404 if no active subscription."""
        user = baker.make(User)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        url = "/api/v1/subscriptions/current/"
        response = client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestSubscriptionStatus:
    """Tests for GET /subscriptions/status/"""

    def test_get_subscription_status(self):
        """Should return subscription status."""
        user = baker.make(User)
        baker.make(
            Subscription,
            user=user,
            plan_type=PlanType.PREMIUM,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=15),
        )
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        url = "/api/v1/subscriptions/status/"
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["data"]["isActive"] is True
        assert resp_data["data"]["planType"] == "PREMIUM"

    def test_get_status_no_subscription(self):
        """Should return null data if no subscription."""
        user = baker.make(User)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        url = "/api/v1/subscriptions/status/"
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["data"] is None


@pytest.mark.django_db
class TestPurchaseList:
    """Tests for GET /purchases/"""

    def test_list_purchases(self):
        """Should return user's purchases."""
        user = baker.make(User)
        ch1 = baker.make(Chapter)
        ch2 = baker.make(Chapter)
        baker.make(Purchase, user=user, chapter=ch1, price_paid=100)
        baker.make(Purchase, user=user, chapter=ch2, price_paid=200)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        url = "/api/v1/purchases/"
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert len(resp_data["data"]["results"]) == 2


@pytest.mark.django_db
class TestChapterPurchase:
    """Tests for POST /chapters/{id}/purchase/"""

    def test_purchase_chapter(self):
        """Should purchase a chapter."""
        user = baker.make(User)
        chapter = baker.make(
            Chapter,
            price=100,
            access_type=AccessType.SUBSCRIPTION,
            status=ChapterStatus.PUBLISHED,
        )
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        url = f"/api/v1/chapters/{chapter.id}/purchase/"
        response = client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert resp_data["data"]["pricePaid"] == 100

    def test_purchase_free_chapter_fails(self):
        """Should fail for FREE chapters."""
        user = baker.make(User)
        chapter = baker.make(Chapter, access_type=AccessType.FREE)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        url = f"/api/v1/chapters/{chapter.id}/purchase/"
        response = client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_purchase_duplicate_fails(self):
        """Should fail if already purchased."""
        user = baker.make(User)
        chapter = baker.make(Chapter, price=100, access_type=AccessType.SUBSCRIPTION)
        baker.make(Purchase, user=user, chapter=chapter, price_paid=100)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        url = f"/api/v1/chapters/{chapter.id}/purchase/"
        response = client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_purchase_nonexistent_chapter(self):
        """Should return 404 for non-existent chapter."""
        user = baker.make(User)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        url = "/api/v1/chapters/99999/purchase/"
        response = client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
