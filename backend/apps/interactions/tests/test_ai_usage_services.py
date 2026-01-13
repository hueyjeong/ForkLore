"""
Service Tests for AI Usage Tracking - TDD approach.

Tests:
- AIUsageService: increment, get_daily_usage, can_use_ai
- Tier-based limits (FREE:5, BASIC:10, PREMIUM:20)
- Date boundary handling (UTC-based)
"""

from datetime import date, timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone
from model_bakery import baker

from apps.interactions.models import (
    AIUsageLog,
    AIActionType,
    Subscription,
    SubscriptionStatus,
    PlanType,
)
from apps.interactions.services import AIUsageService


pytestmark = pytest.mark.django_db


# =============================================================================
# AIUsageService.increment() Tests
# =============================================================================


class TestAIUsageServiceIncrement:
    """Tests for AIUsageService.increment()"""

    def test_increment_creates_new_log(self):
        """Should create a new usage log when none exists for today."""
        service = AIUsageService()
        user = baker.make("users.User")
        today = date.today()

        log = service.increment(user=user, action_type=AIActionType.ASK)

        assert log is not None
        assert log.user == user
        assert log.action_type == AIActionType.ASK
        assert log.usage_date == today
        assert log.request_count == 1

    def test_increment_updates_existing_log(self):
        """Should increment count on existing log for same user/date/action."""
        service = AIUsageService()
        user = baker.make("users.User")
        today = date.today()

        # Create initial log
        existing = baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.ASK,
            request_count=3,
        )

        log = service.increment(user=user, action_type=AIActionType.ASK)

        assert log.id == existing.id
        assert log.request_count == 4

    def test_increment_different_action_types_separate(self):
        """Different action types should have separate logs."""
        service = AIUsageService()
        user = baker.make("users.User")
        today = date.today()

        log1 = service.increment(user=user, action_type=AIActionType.ASK)
        log2 = service.increment(user=user, action_type=AIActionType.WIKI_SUGGEST)

        assert log1.id != log2.id
        assert log1.request_count == 1
        assert log2.request_count == 1

    def test_increment_different_dates_separate(self):
        """Different dates should have separate logs."""
        service = AIUsageService()
        user = baker.make("users.User")
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Create yesterday's log
        baker.make(
            AIUsageLog,
            user=user,
            usage_date=yesterday,
            action_type=AIActionType.ASK,
            request_count=5,
        )

        # Increment today
        log = service.increment(user=user, action_type=AIActionType.ASK)

        assert log.usage_date == today
        assert log.request_count == 1

    def test_increment_with_token_count(self):
        """Should increment token_count when provided."""
        service = AIUsageService()
        user = baker.make("users.User")

        log = service.increment(user=user, action_type=AIActionType.ASK, token_count=100)

        assert log.token_count == 100

        # Increment again with more tokens
        log = service.increment(user=user, action_type=AIActionType.ASK, token_count=50)

        assert log.token_count == 150


# =============================================================================
# AIUsageService.get_daily_usage() Tests
# =============================================================================


class TestAIUsageServiceGetDailyUsage:
    """Tests for AIUsageService.get_daily_usage()"""

    def test_get_daily_usage_returns_count(self):
        """Should return today's usage count for user/action."""
        service = AIUsageService()
        user = baker.make("users.User")
        today = date.today()

        baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.ASK,
            request_count=7,
        )

        count = service.get_daily_usage(user=user, action_type=AIActionType.ASK)

        assert count == 7

    def test_get_daily_usage_no_log_returns_zero(self):
        """Should return 0 when no log exists."""
        service = AIUsageService()
        user = baker.make("users.User")

        count = service.get_daily_usage(user=user, action_type=AIActionType.ASK)

        assert count == 0

    def test_get_daily_usage_ignores_other_dates(self):
        """Should only count today's usage."""
        service = AIUsageService()
        user = baker.make("users.User")
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Yesterday's usage
        baker.make(
            AIUsageLog,
            user=user,
            usage_date=yesterday,
            action_type=AIActionType.ASK,
            request_count=10,
        )

        count = service.get_daily_usage(user=user, action_type=AIActionType.ASK)

        assert count == 0

    def test_get_daily_usage_all_actions(self):
        """Should return total usage across all action types when action_type is None."""
        service = AIUsageService()
        user = baker.make("users.User")
        today = date.today()

        baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.ASK,
            request_count=3,
        )
        baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.WIKI_SUGGEST,
            request_count=2,
        )

        count = service.get_daily_usage(user=user, action_type=None)

        assert count == 5


# =============================================================================
# AIUsageService.can_use_ai() Tests - Tier-based Limits
# =============================================================================


class TestAIUsageServiceCanUseAI:
    """Tests for AIUsageService.can_use_ai() with tier-based limits."""

    def test_free_user_limit_5(self):
        """Free user (no subscription) should have 5 requests/day limit."""
        service = AIUsageService()
        user = baker.make("users.User")
        today = date.today()

        # 4 requests - should be allowed
        baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.ASK,
            request_count=4,
        )

        assert service.can_use_ai(user=user, action_type=AIActionType.ASK) is True

        # 5 requests - should be denied
        AIUsageLog.objects.filter(user=user).update(request_count=5)

        assert service.can_use_ai(user=user, action_type=AIActionType.ASK) is False

    def test_basic_subscriber_limit_10(self):
        """BASIC subscriber should have 10 requests/day limit."""
        service = AIUsageService()
        user = baker.make("users.User")
        today = date.today()

        # Create active BASIC subscription
        baker.make(
            Subscription,
            user=user,
            plan_type=PlanType.BASIC,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
        )

        # 9 requests - should be allowed
        baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.ASK,
            request_count=9,
        )

        assert service.can_use_ai(user=user, action_type=AIActionType.ASK) is True

        # 10 requests - should be denied
        AIUsageLog.objects.filter(user=user).update(request_count=10)

        assert service.can_use_ai(user=user, action_type=AIActionType.ASK) is False

    def test_premium_subscriber_limit_20(self):
        """PREMIUM subscriber should have 20 requests/day limit."""
        service = AIUsageService()
        user = baker.make("users.User")
        today = date.today()

        # Create active PREMIUM subscription
        baker.make(
            Subscription,
            user=user,
            plan_type=PlanType.PREMIUM,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
        )

        # 19 requests - should be allowed
        baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.ASK,
            request_count=19,
        )

        assert service.can_use_ai(user=user, action_type=AIActionType.ASK) is True

        # 20 requests - should be denied
        AIUsageLog.objects.filter(user=user).update(request_count=20)

        assert service.can_use_ai(user=user, action_type=AIActionType.ASK) is False

    def test_expired_subscription_uses_free_limit(self):
        """Expired subscription should use FREE tier limit."""
        service = AIUsageService()
        user = baker.make("users.User")
        today = date.today()

        # Create expired PREMIUM subscription
        baker.make(
            Subscription,
            user=user,
            plan_type=PlanType.PREMIUM,
            status=SubscriptionStatus.EXPIRED,
            expires_at=timezone.now() - timedelta(days=1),
        )

        # 5 requests - should be denied (FREE limit)
        baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.ASK,
            request_count=5,
        )

        assert service.can_use_ai(user=user, action_type=AIActionType.ASK) is False

    def test_cancelled_but_not_expired_uses_plan_limit(self):
        """Cancelled but not expired subscription should still use plan limit."""
        service = AIUsageService()
        user = baker.make("users.User")
        today = date.today()

        # Create cancelled PREMIUM subscription that hasn't expired yet
        baker.make(
            Subscription,
            user=user,
            plan_type=PlanType.PREMIUM,
            status=SubscriptionStatus.CANCELLED,
            expires_at=timezone.now() + timedelta(days=10),
        )

        # 15 requests - should be allowed (still within PREMIUM limit)
        baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.ASK,
            request_count=15,
        )

        assert service.can_use_ai(user=user, action_type=AIActionType.ASK) is True

    def test_no_usage_returns_true(self):
        """Should return True when no usage today."""
        service = AIUsageService()
        user = baker.make("users.User")

        assert service.can_use_ai(user=user, action_type=AIActionType.ASK) is True

    def test_get_remaining_quota(self):
        """Should return remaining quota for user."""
        service = AIUsageService()
        user = baker.make("users.User")
        today = date.today()

        baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.ASK,
            request_count=3,
        )

        remaining = service.get_remaining_quota(user=user, action_type=AIActionType.ASK)

        assert remaining == 2  # FREE limit is 5, used 3


# =============================================================================
# AIUsageService.get_user_tier() Tests
# =============================================================================


class TestAIUsageServiceGetUserTier:
    """Tests for AIUsageService.get_user_tier()"""

    def test_no_subscription_returns_free(self):
        """User without subscription should be FREE tier."""
        service = AIUsageService()
        user = baker.make("users.User")

        tier = service.get_user_tier(user)

        assert tier == "FREE"

    def test_active_basic_returns_basic(self):
        """User with active BASIC subscription should be BASIC tier."""
        service = AIUsageService()
        user = baker.make("users.User")

        baker.make(
            Subscription,
            user=user,
            plan_type=PlanType.BASIC,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
        )

        tier = service.get_user_tier(user)

        assert tier == "BASIC"

    def test_active_premium_returns_premium(self):
        """User with active PREMIUM subscription should be PREMIUM tier."""
        service = AIUsageService()
        user = baker.make("users.User")

        baker.make(
            Subscription,
            user=user,
            plan_type=PlanType.PREMIUM,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
        )

        tier = service.get_user_tier(user)

        assert tier == "PREMIUM"


# =============================================================================
# Date Boundary Tests
# =============================================================================


class TestAIUsageDateBoundary:
    """Tests for date boundary handling."""

    def test_usage_resets_at_midnight_utc(self):
        """Usage should reset at UTC midnight."""
        service = AIUsageService()
        user = baker.make("users.User")
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Yesterday's full usage (at limit)
        baker.make(
            AIUsageLog,
            user=user,
            usage_date=yesterday,
            action_type=AIActionType.ASK,
            request_count=5,
        )

        # Today should be fresh start
        assert service.can_use_ai(user=user, action_type=AIActionType.ASK) is True
        assert service.get_daily_usage(user=user, action_type=AIActionType.ASK) == 0

    def test_usage_counts_per_action_type(self):
        """Each action type has separate daily quota."""
        service = AIUsageService()
        user = baker.make("users.User")
        today = date.today()

        # Max out ASK quota
        baker.make(
            AIUsageLog,
            user=user,
            usage_date=today,
            action_type=AIActionType.ASK,
            request_count=5,
        )

        # WIKI_SUGGEST should still be available
        assert service.can_use_ai(user=user, action_type=AIActionType.ASK) is False
        assert service.can_use_ai(user=user, action_type=AIActionType.WIKI_SUGGEST) is True
