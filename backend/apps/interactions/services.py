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


class ReadingService:
    """Service for managing reading logs."""

    @staticmethod
    def record_reading(user, chapter_id: int, progress: float):
        """
        Record or update reading progress for a chapter.

        Args:
            user: User instance
            chapter_id: ID of chapter being read
            progress: Reading progress (0.0 to 1.0)

        Returns:
            ReadingLog instance
        """
        from apps.interactions.models import ReadingLog
        from apps.contents.models import Chapter

        chapter = Chapter.objects.get(id=chapter_id)
        is_completed = progress >= 1.0

        log, _ = ReadingLog.objects.update_or_create(
            user=user,
            chapter=chapter,
            defaults={
                "progress": progress,
                "is_completed": is_completed,
            },
        )
        return log

    @staticmethod
    def get_recent_reads(user, limit: int = 20):
        """
        Get recently read chapters for a user.

        Args:
            user: User instance
            limit: Maximum number of results

        Returns:
            QuerySet of ReadingLog instances ordered by read_at desc
        """
        from apps.interactions.models import ReadingLog

        return (
            ReadingLog.objects.filter(user=user)
            .select_related("chapter", "chapter__branch", "chapter__branch__novel")
            .order_by("-read_at")[:limit]
        )

    @staticmethod
    def get_continue_reading(user, branch_id: int) -> Dict[str, Any]:
        """
        Get continue reading info for a specific branch.

        Logic:
        1. If user has incomplete reading log, return that chapter
        2. If all read chapters are complete, return next unread chapter
        3. If no history, return first chapter

        Args:
            user: User instance
            branch_id: ID of branch

        Returns:
            Dict with 'chapter' and 'progress' keys
        """
        from apps.interactions.models import ReadingLog
        from apps.contents.models import Chapter

        # Get all chapters in branch ordered by chapter_number
        chapters = Chapter.objects.filter(branch_id=branch_id).order_by("chapter_number")

        if not chapters.exists():
            return {"chapter": None, "progress": 0}

        # Get user's reading logs for this branch
        user_logs = ReadingLog.objects.filter(
            user=user,
            chapter__branch_id=branch_id,
        ).select_related("chapter")

        # Check for incomplete reading (미완독 우선)
        incomplete_log = user_logs.filter(is_completed=False).order_by("-read_at").first()
        if incomplete_log:
            return {
                "chapter": incomplete_log.chapter,
                "progress": incomplete_log.progress,
            }

        # Find the last completed chapter
        last_completed = (
            user_logs.filter(is_completed=True).order_by("-chapter__chapter_number").first()
        )

        if last_completed:
            # Find next chapter after the last completed one
            next_chapter = chapters.filter(
                chapter_number__gt=last_completed.chapter.chapter_number
            ).first()

            if next_chapter:
                return {"chapter": next_chapter, "progress": 0}

            # All chapters completed, return last one
            return {
                "chapter": last_completed.chapter,
                "progress": last_completed.progress,
            }

        # No reading history, return first chapter
        return {"chapter": chapters.first(), "progress": 0}


class BookmarkService:
    """Service for managing bookmarks."""

    @staticmethod
    def add_bookmark(user, chapter_id: int, scroll_position: float = 0, note: str = ""):
        """
        Add or update a bookmark for a chapter.

        Args:
            user: User instance
            chapter_id: ID of chapter to bookmark
            scroll_position: Scroll position (0.0 to 1.0)
            note: Optional note

        Returns:
            Bookmark instance
        """
        from apps.interactions.models import Bookmark
        from apps.contents.models import Chapter

        chapter = Chapter.objects.get(id=chapter_id)

        bookmark, _ = Bookmark.objects.update_or_create(
            user=user,
            chapter=chapter,
            defaults={
                "scroll_position": scroll_position,
                "note": note,
            },
        )
        return bookmark

    @staticmethod
    def remove_bookmark(user, chapter_id: int) -> None:
        """
        Remove a bookmark.

        Args:
            user: User instance
            chapter_id: ID of chapter to remove bookmark from
        """
        from apps.interactions.models import Bookmark

        Bookmark.objects.filter(user=user, chapter_id=chapter_id).delete()

    @staticmethod
    def get_bookmarks(user):
        """
        Get all bookmarks for a user.

        Args:
            user: User instance

        Returns:
            QuerySet of Bookmark instances
        """
        from apps.interactions.models import Bookmark

        return (
            Bookmark.objects.filter(user=user)
            .select_related("chapter", "chapter__branch", "chapter__branch__novel")
            .order_by("-created_at")
        )
