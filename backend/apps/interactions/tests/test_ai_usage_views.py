from datetime import date, timedelta
from typing import Any

import pytest
from django.utils import timezone
from model_bakery import baker
from rest_framework.response import Response
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.interactions.models import (
    AIActionType,
    AIUsageLog,
    PlanType,
    Subscription,
    SubscriptionStatus,
)
from apps.users.models import User

pytestmark = pytest.mark.django_db


def get_auth_client(user: User) -> APIClient:
    """Create authenticated API client."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


def get_response_data(response: Response) -> Any:
    """Extract data from wrapped response or return as-is."""
    json_data = response.json()
    # Response is wrapped in {success, message, data, timestamp}
    if "data" in json_data and isinstance(json_data.get("data"), dict):
        return json_data["data"]
    return json_data


# =============================================================================
# GET /api/v1/users/me/ai-usage/ Tests
# =============================================================================


class TestGetAIUsageStatus:
    """Tests for GET /api/v1/users/me/ai-usage/"""

    def test_get_usage_status_authenticated(self) -> None:
        """Should return usage status for authenticated user."""
        user = baker.make("users.User")
        client = get_auth_client(user)
        today = date.today()

        # Create some usage
        baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.ASK,
            request_count=3,
        )

        url = "/api/v1/users/me/ai-usage/"
        response = client.get(url)

        assert response.status_code == 200, f"Response: {response.content}"
        data = get_response_data(response)
        assert data["tier"] == "FREE"
        # Note: camelCase keys due to renderer
        assert data.get("dailyLimit") == 5 or data.get("daily_limit") == 5
        usage_by_action = data.get("usageByAction", data.get("usage_by_action", {}))
        assert usage_by_action["ASK"]["used"] == 3
        assert usage_by_action["ASK"]["remaining"] == 2

    def test_get_usage_status_premium_user(self) -> None:
        """Premium user should have higher limits."""
        user = baker.make("users.User")
        client = get_auth_client(user)

        # Create premium subscription
        baker.make(
            Subscription,
            user=user,
            plan_type=PlanType.PREMIUM,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
        )

        url = "/api/v1/users/me/ai-usage/"
        response = client.get(url)

        assert response.status_code == 200
        data = get_response_data(response)
        assert data["tier"] == "PREMIUM"
        assert data.get("dailyLimit") == 20 or data.get("daily_limit") == 20

    def test_get_usage_status_unauthenticated(self) -> None:
        """Should return 401 for unauthenticated request."""
        client = APIClient()
        url = "/api/v1/users/me/ai-usage/"
        response = client.get(url)

        assert response.status_code == 401


# =============================================================================
# POST /api/v1/ai/check-limit/ Tests
# =============================================================================


class TestCheckAILimit:
    """Tests for POST /api/v1/ai/check-limit/"""

    def test_check_limit_allowed(self) -> None:
        """Should return allowed=True when under limit."""
        user = baker.make("users.User")
        client = get_auth_client(user)

        url = "/api/v1/ai/check-limit/"
        response = client.post(url, {"action_type": "ASK"})

        assert response.status_code == 200
        data = get_response_data(response)
        assert data["allowed"] is True
        assert data["remaining"] == 5

    def test_check_limit_denied(self) -> None:
        """Should return allowed=False when at limit."""
        user = baker.make("users.User")
        client = get_auth_client(user)
        today = date.today()

        # Max out usage
        baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.ASK,
            request_count=5,
        )

        url = "/api/v1/ai/check-limit/"
        response = client.post(url, {"action_type": "ASK"})

        assert response.status_code == 200
        data = get_response_data(response)
        assert data["allowed"] is False
        assert data["remaining"] == 0

    def test_check_limit_returns_429_when_over(self) -> None:
        """Optional: Return 429 when over limit for AI endpoints."""
        user = baker.make("users.User")
        client = get_auth_client(user)
        today = date.today()

        # Max out usage
        baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.ASK,
            request_count=5,
        )

        url = "/api/v1/ai/check-limit/"
        response = client.post(url, {"action_type": "ASK", "enforce": True})

        # When enforce=True, should return 429
        assert response.status_code == 429
        data = response.json()
        detail = data.get("detail", "")
        assert "limit" in detail.lower() or "한도" in detail

    def test_check_limit_invalid_action_type(self) -> None:
        """Should return 400 for invalid action type."""
        user = baker.make("users.User")
        client = get_auth_client(user)

        url = "/api/v1/ai/check-limit/"
        response = client.post(url, {"action_type": "INVALID"})

        assert response.status_code == 400

    def test_check_limit_unauthenticated(self) -> None:
        """Should return 401 for unauthenticated request."""
        client = APIClient()
        url = "/api/v1/ai/check-limit/"
        response = client.post(url, {"action_type": "ASK"})

        assert response.status_code == 401


# =============================================================================
# POST /api/v1/ai/record-usage/ Tests
# =============================================================================


class TestRecordAIUsage:
    """Tests for POST /api/v1/ai/record-usage/"""

    def test_record_usage_success(self) -> None:
        """Should record usage and return updated status."""
        user = baker.make("users.User")
        client = get_auth_client(user)

        url = "/api/v1/ai/record-usage/"
        response = client.post(url, {"action_type": "ASK"})

        assert response.status_code == 200
        data = get_response_data(response)
        assert data["used"] == 1
        assert data["remaining"] == 4

    def test_record_usage_increments(self) -> None:
        """Should increment existing usage."""
        user = baker.make("users.User")
        client = get_auth_client(user)
        today = date.today()

        baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.ASK,
            request_count=2,
        )

        url = "/api/v1/ai/record-usage/"
        response = client.post(url, {"action_type": "ASK"})

        assert response.status_code == 200
        data = get_response_data(response)
        assert data["used"] == 3
        assert data["remaining"] == 2

    def test_record_usage_with_token_count(self) -> None:
        """Should record token count if provided."""
        user = baker.make("users.User")
        client = get_auth_client(user)

        url = "/api/v1/ai/record-usage/"
        response = client.post(url, {"action_type": "ASK", "token_count": 150})

        assert response.status_code == 200

        log = AIUsageLog.objects.get(user=user)
        assert log.token_count == 150

    def test_record_usage_blocked_at_limit(self) -> None:
        """Should return 429 when recording would exceed limit."""
        user = baker.make("users.User")
        client = get_auth_client(user)
        today = date.today()

        # At limit
        baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.ASK,
            request_count=5,
        )

        url = "/api/v1/ai/record-usage/"
        response = client.post(url, {"action_type": "ASK"})

        assert response.status_code == 429

    def test_record_usage_unauthenticated(self) -> None:
        """Should return 401 for unauthenticated request."""
        client = APIClient()
        url = "/api/v1/ai/record-usage/"
        response = client.post(url, {"action_type": "ASK"})

        assert response.status_code == 401
