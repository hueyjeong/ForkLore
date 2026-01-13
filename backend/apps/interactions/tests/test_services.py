"""
Service Tests for Subscription system - TDD approach.

Tests:
- AccessService: can_access_chapter logic
- SubscriptionService: subscribe, cancel, get_status
- PurchaseService: purchase, get_purchase_list
"""

from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker

from apps.contents.models import AccessType, Chapter, ChapterStatus
from apps.interactions.models import PlanType, Purchase, Subscription, SubscriptionStatus
from apps.interactions.services import AccessService, PurchaseService, SubscriptionService
from apps.novels.models import Branch
from apps.users.models import User

# =============================================================================
# AccessService Tests
# =============================================================================


@pytest.mark.django_db
class TestAccessServiceCanAccessChapter:
    """Tests for AccessService.can_access_chapter()"""

    def test_free_chapter_accessible_by_anyone(self):
        """FREE chapters should be accessible to anyone."""
        service = AccessService()
        user = baker.make(User)
        chapter = baker.make(Chapter, access_type=AccessType.FREE, status=ChapterStatus.PUBLISHED)

        result = service.can_access_chapter(user=user, chapter=chapter)

        assert result is True

    def test_free_chapter_accessible_without_login(self):
        """FREE chapters should be accessible without login."""
        service = AccessService()
        chapter = baker.make(Chapter, access_type=AccessType.FREE, status=ChapterStatus.PUBLISHED)

        result = service.can_access_chapter(user=None, chapter=chapter)

        assert result is True

    def test_author_can_access_own_chapter(self):
        """Author should access their own SUBSCRIPTION chapters."""
        service = AccessService()
        author = baker.make(User)
        branch = baker.make(Branch, author=author)
        chapter = baker.make(
            Chapter,
            branch=branch,
            access_type=AccessType.SUBSCRIPTION,
            status=ChapterStatus.PUBLISHED,
        )

        result = service.can_access_chapter(user=author, chapter=chapter)

        assert result is True

    def test_subscriber_can_access_subscription_chapter(self):
        """User with active subscription can access SUBSCRIPTION chapters."""
        service = AccessService()
        user = baker.make(User)
        chapter = baker.make(
            Chapter,
            access_type=AccessType.SUBSCRIPTION,
            status=ChapterStatus.PUBLISHED,
        )
        baker.make(
            Subscription,
            user=user,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
        )

        result = service.can_access_chapter(user=user, chapter=chapter)

        assert result is True

    def test_expired_subscription_cannot_access(self):
        """User with expired subscription cannot access SUBSCRIPTION chapters."""
        service = AccessService()
        user = baker.make(User)
        chapter = baker.make(
            Chapter,
            access_type=AccessType.SUBSCRIPTION,
            status=ChapterStatus.PUBLISHED,
        )
        baker.make(
            Subscription,
            user=user,
            status=SubscriptionStatus.EXPIRED,
            expires_at=timezone.now() - timedelta(days=1),
        )

        result = service.can_access_chapter(user=user, chapter=chapter)

        assert result is False

    def test_purchased_chapter_accessible(self):
        """User who purchased the chapter can access it."""
        service = AccessService()
        user = baker.make(User)
        chapter = baker.make(
            Chapter,
            access_type=AccessType.SUBSCRIPTION,
            status=ChapterStatus.PUBLISHED,
        )
        baker.make(Purchase, user=user, chapter=chapter, price_paid=100)

        result = service.can_access_chapter(user=user, chapter=chapter)

        assert result is True

    def test_no_subscription_no_purchase_denied(self):
        """User without subscription or purchase cannot access SUBSCRIPTION chapter."""
        service = AccessService()
        user = baker.make(User)
        chapter = baker.make(
            Chapter,
            access_type=AccessType.SUBSCRIPTION,
            status=ChapterStatus.PUBLISHED,
        )

        result = service.can_access_chapter(user=user, chapter=chapter)

        assert result is False

    def test_unauthenticated_denied_for_subscription_chapter(self):
        """Unauthenticated user cannot access SUBSCRIPTION chapters."""
        service = AccessService()
        chapter = baker.make(
            Chapter,
            access_type=AccessType.SUBSCRIPTION,
            status=ChapterStatus.PUBLISHED,
        )

        result = service.can_access_chapter(user=None, chapter=chapter)

        assert result is False


# =============================================================================
# SubscriptionService Tests
# =============================================================================


@pytest.mark.django_db
class TestSubscriptionServiceSubscribe:
    """Tests for SubscriptionService.subscribe()"""

    def test_create_new_subscription(self):
        """Should create a new subscription for user."""
        service = SubscriptionService()
        user = baker.make(User)

        subscription = service.subscribe(user=user, plan_type=PlanType.BASIC, days=30)

        assert subscription.id is not None
        assert subscription.user == user
        assert subscription.plan_type == PlanType.BASIC
        assert subscription.status == SubscriptionStatus.ACTIVE
        assert subscription.expires_at > timezone.now()

    def test_extend_existing_subscription(self):
        """Should extend existing active subscription."""
        service = SubscriptionService()
        user = baker.make(User)
        existing_expires = timezone.now() + timedelta(days=10)
        baker.make(
            Subscription,
            user=user,
            status=SubscriptionStatus.ACTIVE,
            expires_at=existing_expires,
        )

        subscription = service.subscribe(user=user, plan_type=PlanType.BASIC, days=30)

        # Should extend from existing expiry
        assert subscription.expires_at > existing_expires + timedelta(days=29)


@pytest.mark.django_db
class TestSubscriptionServiceCancel:
    """Tests for SubscriptionService.cancel()"""

    def test_cancel_subscription(self):
        """Should cancel active subscription."""
        service = SubscriptionService()
        user = baker.make(User)
        subscription = baker.make(
            Subscription,
            user=user,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
        )

        result = service.cancel(user=user)

        subscription.refresh_from_db()
        assert result is True
        assert subscription.status == SubscriptionStatus.CANCELLED
        assert subscription.cancelled_at is not None

    def test_cancel_no_subscription_returns_false(self):
        """Should return False if no active subscription."""
        service = SubscriptionService()
        user = baker.make(User)

        result = service.cancel(user=user)

        assert result is False


@pytest.mark.django_db
class TestSubscriptionServiceGetStatus:
    """Tests for SubscriptionService.get_status()"""

    def test_get_active_subscription_status(self):
        """Should return active subscription details."""
        service = SubscriptionService()
        user = baker.make(User)
        expires_at = timezone.now() + timedelta(days=15)
        baker.make(
            Subscription,
            user=user,
            plan_type=PlanType.PREMIUM,
            status=SubscriptionStatus.ACTIVE,
            expires_at=expires_at,
        )

        result = service.get_status(user=user)

        assert result is not None
        assert result["is_active"] is True
        assert result["plan_type"] == PlanType.PREMIUM

    def test_get_status_no_subscription(self):
        """Should return None if no subscription."""
        service = SubscriptionService()
        user = baker.make(User)

        result = service.get_status(user=user)

        assert result is None

    def test_expired_subscription_updates_status(self):
        """Should update status to EXPIRED if expires_at passed."""
        service = SubscriptionService()
        user = baker.make(User)
        baker.make(
            Subscription,
            user=user,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() - timedelta(days=1),
        )

        result = service.get_status(user=user)

        assert result is not None
        assert result["is_active"] is False


# =============================================================================
# PurchaseService Tests
# =============================================================================


@pytest.mark.django_db
class TestPurchaseServicePurchase:
    """Tests for PurchaseService.purchase()"""

    def test_purchase_chapter(self):
        """Should create a purchase record."""
        service = PurchaseService()
        user = baker.make(User)
        chapter = baker.make(Chapter, price=100, access_type=AccessType.SUBSCRIPTION)

        purchase = service.purchase(user=user, chapter=chapter)

        assert purchase.id is not None
        assert purchase.user == user
        assert purchase.chapter == chapter
        assert purchase.price_paid == 100

    def test_purchase_duplicate_raises_error(self):
        """Should raise error if already purchased."""
        service = PurchaseService()
        user = baker.make(User)
        chapter = baker.make(Chapter, price=100, access_type=AccessType.SUBSCRIPTION)
        baker.make(Purchase, user=user, chapter=chapter, price_paid=100)

        with pytest.raises(ValueError, match="이미 소장"):
            service.purchase(user=user, chapter=chapter)

    def test_purchase_free_chapter_raises_error(self):
        """Should raise error for FREE chapters."""
        service = PurchaseService()
        user = baker.make(User)
        chapter = baker.make(Chapter, access_type=AccessType.FREE)

        with pytest.raises(ValueError, match="무료"):
            service.purchase(user=user, chapter=chapter)


@pytest.mark.django_db
class TestPurchaseServiceGetPurchaseList:
    """Tests for PurchaseService.get_purchase_list()"""

    def test_get_purchase_list(self):
        """Should return all purchases for user."""
        service = PurchaseService()
        user = baker.make(User)
        ch1 = baker.make(Chapter)
        ch2 = baker.make(Chapter)
        baker.make(Purchase, user=user, chapter=ch1, price_paid=100)
        baker.make(Purchase, user=user, chapter=ch2, price_paid=200)

        result = service.get_purchase_list(user=user)

        assert len(result) == 2

    def test_get_purchase_list_excludes_other_users(self):
        """Should only return purchases for the specified user."""
        service = PurchaseService()
        user1 = baker.make(User)
        user2 = baker.make(User)
        ch = baker.make(Chapter)
        baker.make(Purchase, user=user1, chapter=ch, price_paid=100)
        baker.make(Purchase, user=user2, chapter=ch, price_paid=100)

        result = service.get_purchase_list(user=user1)

        assert len(result) == 1
