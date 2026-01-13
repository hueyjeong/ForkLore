"""
Services for interactions app.

Contains:
- AccessService: Chapter access permission checking
- SubscriptionService: Subscription management
- PurchaseService: Chapter purchase management
"""

from datetime import timedelta
from typing import Optional, Dict, Any

from django.db.models import QuerySet
from django.utils import timezone

from apps.contents.models import Chapter, AccessType
from apps.interactions.models import Subscription, Purchase, SubscriptionStatus, PlanType


class AccessService:
    """Service for checking chapter access permissions."""

    def can_access_chapter(self, user, chapter: Chapter) -> bool:
        """
        Check if a user can access a chapter.

        Access rules:
        1. FREE chapters are accessible to everyone
        2. Author can access their own chapters
        3. Active subscription allows access
        4. Purchased chapter allows access

        Args:
            user: User instance or None
            chapter: Chapter to check access for

        Returns:
            True if access is allowed, False otherwise
        """
        # FREE chapters are always accessible
        if chapter.access_type == AccessType.FREE:
            return True

        # SUBSCRIPTION chapters require authentication
        if user is None:
            return False

        # Author can access their own chapters
        if chapter.branch.author_id == user.id:
            return True

        # Check for active subscription
        if self._has_active_subscription(user):
            return True

        # Check if chapter was purchased
        if self._has_purchased(user, chapter):
            return True

        return False

    def _has_active_subscription(self, user) -> bool:
        """Check if user has an active, non-expired subscription."""
        return Subscription.objects.filter(
            user=user,
            status=SubscriptionStatus.ACTIVE,
            expires_at__gt=timezone.now(),
        ).exists()

    def _has_purchased(self, user, chapter: Chapter) -> bool:
        """Check if user has purchased the chapter."""
        return Purchase.objects.filter(user=user, chapter=chapter).exists()


class SubscriptionService:
    """Service for managing subscriptions."""

    def subscribe(
        self,
        user,
        plan_type: str = PlanType.BASIC,
        days: int = 30,
        payment_id: str = "",
    ) -> Subscription:
        """
        Create or extend a subscription.

        If user has an active subscription, extends from current expiry.
        Otherwise, creates a new subscription starting now.

        Args:
            user: User instance
            plan_type: BASIC or PREMIUM
            days: Number of days to subscribe
            payment_id: Payment reference ID

        Returns:
            Subscription instance
        """
        now = timezone.now()

        # Check for existing active subscription
        existing = Subscription.objects.filter(
            user=user,
            status=SubscriptionStatus.ACTIVE,
            expires_at__gt=now,
        ).first()

        if existing:
            # Extend existing subscription
            existing.expires_at = existing.expires_at + timedelta(days=days)
            existing.plan_type = plan_type
            if payment_id:
                existing.payment_id = payment_id
            existing.save()
            return existing
        else:
            # Create new subscription
            return Subscription.objects.create(
                user=user,
                plan_type=plan_type,
                expires_at=now + timedelta(days=days),
                payment_id=payment_id,
                status=SubscriptionStatus.ACTIVE,
            )

    def cancel(self, user) -> bool:
        """
        Cancel user's active subscription.

        Sets status to CANCELLED and records cancellation time.
        Subscription remains valid until expires_at.

        Args:
            user: User instance

        Returns:
            True if cancelled, False if no active subscription
        """
        subscription = Subscription.objects.filter(
            user=user,
            status=SubscriptionStatus.ACTIVE,
        ).first()

        if not subscription:
            return False

        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = timezone.now()
        subscription.auto_renew = False
        subscription.save()
        return True

    def get_status(self, user) -> Optional[Dict[str, Any]]:
        """
        Get user's subscription status.

        Also updates status to EXPIRED if expires_at has passed.

        Args:
            user: User instance

        Returns:
            Dict with subscription info or None if no subscription
        """
        subscription = Subscription.objects.filter(user=user).order_by("-created_at").first()

        if not subscription:
            return None

        now = timezone.now()

        # Update status if expired
        if subscription.status == SubscriptionStatus.ACTIVE and subscription.expires_at <= now:
            subscription.status = SubscriptionStatus.EXPIRED
            subscription.save(update_fields=["status", "updated_at"])

        is_active = (
            subscription.status == SubscriptionStatus.ACTIVE and subscription.expires_at > now
        )

        return {
            "id": subscription.id,
            "is_active": is_active,
            "plan_type": subscription.plan_type,
            "status": subscription.status,
            "started_at": subscription.started_at,
            "expires_at": subscription.expires_at,
            "cancelled_at": subscription.cancelled_at,
            "auto_renew": subscription.auto_renew,
        }


class PurchaseService:
    """Service for managing chapter purchases."""

    def purchase(self, user, chapter: Chapter) -> Purchase:
        """
        Purchase a chapter for permanent access.

        Args:
            user: User instance
            chapter: Chapter to purchase

        Returns:
            Purchase instance

        Raises:
            ValueError: If chapter is FREE or already purchased
        """
        if chapter.access_type == AccessType.FREE:
            raise ValueError("무료 회차는 구매할 수 없습니다.")

        if Purchase.objects.filter(user=user, chapter=chapter).exists():
            raise ValueError("이미 소장한 회차입니다.")

        return Purchase.objects.create(
            user=user,
            chapter=chapter,
            price_paid=chapter.price,
        )

    def get_purchase_list(self, user) -> QuerySet[Purchase]:
        """
        Get all purchases for a user.

        Args:
            user: User instance

        Returns:
            QuerySet of Purchase instances
        """
        return Purchase.objects.filter(user=user).select_related("chapter").order_by("-created_at")
