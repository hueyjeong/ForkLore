"""
Services for interactions app.

Contains:
- AccessService: Chapter access permission checking
- SubscriptionService: Subscription management
- PurchaseService: Chapter purchase management
"""

from datetime import timedelta
from typing import Any

from django.db import DatabaseError, IntegrityError, transaction
from django.db.models import QuerySet
from django.utils import timezone

from apps.contents.models import AccessType, Chapter
from apps.interactions.constants import PLAN_PRICES
from apps.interactions.models import (
    AIUsageLog,
    PlanType,
    Purchase,
    Report,
    Subscription,
    SubscriptionStatus,
)
from apps.interactions.services.payment_service import PaymentService
from apps.users.models import User


class AccessService:
    """Service for checking chapter access permissions."""

    def can_access_chapter(self, user: User, chapter: Chapter) -> bool:
        """
        Check if a user can access a chapter.

        Access rules:
        1. FREE chapters are accessible to everyone
        2. Author can access their own chapters
        3. Active subscription allows access
        4. Purchased chapter allows access

        Args:
            user instance or None
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

    def _has_active_subscription(self, user: User) -> bool:
        """Check if user has an active, non-expired subscription."""
        return Subscription.objects.filter(
            user=user,
            status=SubscriptionStatus.ACTIVE,
            expires_at__gt=timezone.now(),
        ).exists()

    def _has_purchased(self, user: User, chapter: Chapter) -> bool:
        """Check if user has purchased the chapter."""
        return Purchase.objects.filter(user=user, chapter=chapter).exists()


class SubscriptionService:
    """Service for managing subscriptions."""

    def subscribe(
        self,
        user: User,
        plan_type: str = PlanType.BASIC,
        days: int = 30,
        payment_id: str = "",
        order_id: str = "",
    ) -> Subscription:
        """
        Create or extend a subscription.

        If user has an active subscription, extends from current expiry.
        Otherwise, creates a new subscription starting now.

        Args:
            user instance
            plan_type: BASIC or PREMIUM
            days: Number of days to subscribe
            payment_id: Payment reference ID
            order_id: Order ID for payment

        Returns:
            Subscription instance

        Raises:
            PaymentFailedException: If payment fails
        """
        now = timezone.now()

        # Determine price and process payment
        price = PLAN_PRICES.get(plan_type, 0)

        # Track whether payment was successfully confirmed
        # Only set to True AFTER confirm_payment succeeds
        payment_confirmed = False

        # Confirm payment OUTSIDE try block
        # PaymentFailedException will propagate up without triggering cancel
        if price > 0 and payment_id and order_id:
            PaymentService().confirm_payment(
                payment_key=payment_id,
                order_id=order_id,
                amount=price,
            )
            payment_confirmed = True

        try:
            with transaction.atomic():
                # Check for existing active subscription
                existing = (
                    Subscription.objects.filter(
                        user=user,
                        status=SubscriptionStatus.ACTIVE,
                        expires_at__gt=now,
                    )
                    .select_for_update()
                    .first()
                )

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
        except (IntegrityError, DatabaseError, ValueError) as e:
            # Only cancel payment if it was successfully confirmed
            # This prevents trying to cancel a payment that was never approved
            if payment_confirmed:
                PaymentService().cancel_payment(payment_id, "System Error: Transaction failed")
            raise e

    def cancel(self, user: User) -> bool:
        """
        Cancel user's active subscription.

        Sets status to CANCELLED and records cancellation time.
        Subscription remains valid until expires_at.

        Args:
            user instance

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

    def get_status(self, user: User) -> dict[str, Any] | None:
        """
        Get user's subscription status.

        Also updates status to EXPIRED if expires_at has passed.

        Args:
            user instance

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

    def purchase(self, user: User, chapter: Chapter) -> Purchase:
        """
        Purchase a chapter for permanent access.

        Args:
            user instance
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

    def get_purchase_list(self, user: User) -> QuerySet[Purchase]:
        """
        Get all purchases for a user.

        Args:
            user instance

        Returns:
            QuerySet of Purchase instances
        """
        return Purchase.objects.filter(user=user).select_related("chapter").order_by("-created_at")


class ReadingService:
    """Service for managing reading logs."""

    @staticmethod
    def record_reading(user: User, chapter_id: int, progress: float) -> Any:
        """
        Record or update reading progress for a chapter.

        Args:
            user instance
            chapter_id: ID of chapter being read
            progress: Reading progress (0.0 to 1.0)

        Returns:
            ReadingLog instance
        """
        from apps.contents.models import Chapter
        from apps.interactions.models import ReadingLog

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
    def get_recent_reads(user: User, limit: int = 20) -> QuerySet:
        """
        Get recently read chapters for a user.

        Args:
            user instance
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
    def get_continue_reading(user: User, branch_id: int) -> dict[str, Any]:
        """
        Get continue reading info for a specific branch.

        Logic:
        1. If user has incomplete reading log, return that chapter
        2. If all read chapters are complete, return next unread chapter
        3. If no history, return first chapter

        Args:
            user instance
            branch_id: ID of branch

        Returns:
            Dict with 'chapter' and 'progress' keys
        """
        from apps.contents.models import Chapter
        from apps.interactions.models import ReadingLog

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
    def add_bookmark(
        user: User, chapter_id: int, scroll_position: float = 0, note: str = ""
    ) -> Any:
        """
        Add or update a bookmark for a chapter.

        Args:
            user instance
            chapter_id: ID of chapter to bookmark
            scroll_position: Scroll position (0.0 to 1.0)
            note: Optional note

        Returns:
            Bookmark instance
        """
        from apps.contents.models import Chapter
        from apps.interactions.models import Bookmark

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
    def remove_bookmark(user: User, chapter_id: int) -> None:
        """
        Remove a bookmark.

        Args:
            user instance
            chapter_id: ID of chapter to remove bookmark from
        """
        from apps.interactions.models import Bookmark

        Bookmark.objects.filter(user=user, chapter_id=chapter_id).delete()

    @staticmethod
    def get_bookmarks(user: User) -> QuerySet:
        """
        Get all bookmarks for a user.

        Args:
            user instance

        Returns:
            QuerySet of Bookmark instances
        """
        from apps.interactions.models import Bookmark

        return (
            Bookmark.objects.filter(user=user)
            .select_related("chapter", "chapter__branch", "chapter__branch__novel")
            .order_by("-created_at")
        )


class CommentService:
    """Service for managing comments."""

    @staticmethod
    def create(
        user: User,
        chapter_id: int,
        content: str,
        parent_id: int = None,
        is_spoiler: bool = False,
        paragraph_index: int = None,
        selection_start: int = None,
        selection_end: int = None,
        quoted_text: str = "",
    ) -> Any:
        """
        Create a new comment.

        Args:
            user instance
            chapter_id: ID of chapter to comment on
            content: Comment content
            parent_id: Parent comment ID for replies
            is_spoiler: Whether comment contains spoilers
            paragraph_index: Index of paragraph for paragraph comments
            selection_start: Start of text selection
            selection_end: End of text selection
            quoted_text: Quoted text from chapter

        Returns:
            Comment instance

        Raises:
            ValueError: If selection_start >= selection_end
        """
        from apps.contents.models import Chapter
        from apps.interactions.models import Comment

        # Validate selection range
        if selection_start is not None and selection_end is not None:
            if selection_start >= selection_end:
                raise ValueError("selection_start must be less than selection_end")

        chapter = Chapter.objects.get(id=chapter_id)
        parent = Comment.objects.get(id=parent_id) if parent_id else None

        comment = Comment.objects.create(
            user=user,
            chapter=chapter,
            parent=parent,
            content=content,
            is_spoiler=is_spoiler,
            paragraph_index=paragraph_index,
            selection_start=selection_start,
            selection_end=selection_end,
            quoted_text=quoted_text,
        )
        return comment

    @staticmethod
    def update(comment_id: int, user: User, content: str = None, is_spoiler: bool = None) -> Any:
        """
        Update a comment.

        Args:
            comment_id: ID of comment to update
            user instance (must be owner)
            content: New content
            is_spoiler: New spoiler status

        Returns:
            Updated Comment instance

        Raises:
            PermissionError: If user is not the owner
        """
        from apps.interactions.models import Comment

        comment = Comment.objects.get(id=comment_id)

        if comment.user != user:
            raise PermissionError("댓글 작성자만 수정할 수 있습니다.")

        if content is not None:
            comment.content = content
        if is_spoiler is not None:
            comment.is_spoiler = is_spoiler

        comment.save()
        return comment

    @staticmethod
    def delete(comment_id: int, user: User) -> None:
        """
        Soft delete a comment.

        Args:
            comment_id: ID of comment to delete
            user instance (must be owner)

        Raises:
            PermissionError: If user is not the owner
        """
        from django.utils import timezone

        from apps.interactions.models import Comment

        comment = Comment.objects.get(id=comment_id)

        if comment.user != user:
            raise PermissionError("댓글 작성자만 삭제할 수 있습니다.")

        comment.deleted_at = timezone.now()
        comment.save()

    @staticmethod
    def list(chapter_id: int, paragraph_index: int = None) -> list:
        """
        List comments for a chapter.

        Args:
            chapter_id: ID of chapter
            paragraph_index: Filter by paragraph index

        Returns:
            QuerySet of Comment instances
        """
        from apps.interactions.models import Comment

        queryset = (
            Comment.objects.filter(
                chapter_id=chapter_id,
                deleted_at__isnull=True,
            )
            .select_related("user", "parent")
            .order_by("-created_at")
        )

        if paragraph_index is not None:
            queryset = queryset.filter(paragraph_index=paragraph_index)

        return list(queryset)

    @staticmethod
    def pin(comment_id: int, user: User) -> Any:
        """
        Pin a comment (author only).

        Args:
            comment_id: ID of comment to pin
            user instance (must be branch author)

        Returns:
            Pinned Comment instance

        Raises:
            PermissionError: If user is not the branch author
        """
        from apps.interactions.models import Comment

        comment = Comment.objects.select_related("chapter__branch").get(id=comment_id)

        if comment.chapter.branch.author != user:
            raise PermissionError("작가만 댓글을 고정할 수 있습니다.")

        comment.is_pinned = True
        comment.save()
        return comment

    @staticmethod
    def unpin(comment_id: int, user: User) -> Any:
        """
        Unpin a comment (author only).

        Args:
            comment_id: ID of comment to unpin
            user instance (must be branch author)

        Returns:
            Unpinned Comment instance

        Raises:
            PermissionError: If user is not the branch author
        """
        from apps.interactions.models import Comment

        comment = Comment.objects.select_related("chapter__branch").get(id=comment_id)

        if comment.chapter.branch.author != user:
            raise PermissionError("작가만 댓글 고정을 해제할 수 있습니다.")

        comment.is_pinned = False
        comment.save()
        return comment


class LikeService:
    """Service for managing likes."""

    @staticmethod
    def toggle(user: User, target: Any) -> dict[str, Any]:
        """
        Toggle like on a target (comment, chapter, etc.).

        Args:
            user instance
            target: Model instance to like (Comment, Chapter, etc.)

        Returns:
            Dict with 'liked' (bool) and 'like_count' (int)
        """
        from django.contrib.contenttypes.models import ContentType

        from apps.interactions.models import Like

        content_type = ContentType.objects.get_for_model(target)

        like, created = Like.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=target.id,
        )

        if not created:
            # Already liked, so unlike
            like.delete()
            liked = False
        else:
            liked = True

        # Update like_count if target has it
        if hasattr(target, "like_count"):
            if liked:
                target.like_count += 1
            else:
                target.like_count = max(0, target.like_count - 1)
            target.save(update_fields=["like_count", "updated_at"])

        return {
            "liked": liked,
            "like_count": getattr(target, "like_count", None),
        }

    @staticmethod
    def get_like_status(user: User, target: Any) -> bool:
        """
        Check if user has liked a target.

        Args:
            user instance
            target: Model instance to check

        Returns:
            True if liked, False otherwise
        """
        from django.contrib.contenttypes.models import ContentType

        from apps.interactions.models import Like

        if not user or not user.is_authenticated:
            return False

        content_type = ContentType.objects.get_for_model(target)
        return Like.objects.filter(
            user=user,
            content_type=content_type,
            object_id=target.id,
        ).exists()


class ReportService:
    """Service for managing reports."""

    @staticmethod
    def create_report(reporter: User, target: Any, reason: str, description: str = "") -> "Report":
        """
        Create a report for a target (comment, chapter, etc.).

        Args:
            reporter submitting the report
            target: Model instance to report (Comment, Chapter, etc.)
            reason: ReportReason value
            description: Optional detailed description

        Returns:
            Report instance

        Raises:
            ValueError: If user has already reported this target
        """
        from django.contrib.contenttypes.models import ContentType

        from apps.interactions.models import Report, ReportStatus

        content_type = ContentType.objects.get_for_model(target)

        # Check for duplicate report
        if Report.objects.filter(
            reporter=reporter,
            content_type=content_type,
            object_id=target.id,
        ).exists():
            raise ValueError("이미 신고한 대상입니다")

        return Report.objects.create(
            reporter=reporter,
            content_type=content_type,
            object_id=target.id,
            reason=reason,
            description=description,
            status=ReportStatus.PENDING,
        )

    @staticmethod
    def admin_resolve(report_id: int, resolver: User, note: str = "") -> "Report":
        """
        Resolve a report (admin only).

        Args:
            report_id: ID of report to resolve
            resolver: Admin user processing the report
            note: Optional resolution note

        Returns:
            Updated Report instance

        Raises:
            PermissionError: If resolver is not admin
            ValueError: If report is already processed
        """
        from apps.interactions.models import Report, ReportStatus

        if not resolver.is_staff:
            raise PermissionError("관리자만 신고를 처리할 수 있습니다")

        report = Report.objects.get(id=report_id)

        if report.status != ReportStatus.PENDING:
            raise ValueError("이미 처리된 신고입니다")

        report.status = ReportStatus.RESOLVED
        report.resolver = resolver
        report.resolution_note = note
        report.resolved_at = timezone.now()
        report.save()

        return report

    @staticmethod
    def admin_reject(report_id: int, resolver: User, note: str = "") -> "Report":
        """
        Reject a report (admin only).

        Args:
            report_id: ID of report to reject
            resolver: Admin user processing the report
            note: Optional rejection note

        Returns:
            Updated Report instance

        Raises:
            PermissionError: If resolver is not admin
            ValueError: If report is already processed
        """
        from apps.interactions.models import Report, ReportStatus

        if not resolver.is_staff:
            raise PermissionError("관리자만 신고를 처리할 수 있습니다")

        report = Report.objects.get(id=report_id)

        if report.status != ReportStatus.PENDING:
            raise ValueError("이미 처리된 신고입니다")

        report.status = ReportStatus.REJECTED
        report.resolver = resolver
        report.resolution_note = note
        report.resolved_at = timezone.now()
        report.save()

        return report

    @staticmethod
    def list_pending() -> list:
        """
        List all pending reports.

        Returns:
            List of pending Report instances
        """
        from apps.interactions.models import Report, ReportStatus

        return list(
            Report.objects.filter(status=ReportStatus.PENDING)
            .select_related("reporter", "resolver", "content_type")
            .order_by("-created_at")
        )

    @staticmethod
    def list_all(status: str = None) -> list:
        """
        List all reports, optionally filtered by status.

        Args:
            status: Optional ReportStatus to filter by

        Returns:
            List of Report instances
        """
        from apps.interactions.models import Report

        queryset = Report.objects.select_related("reporter", "resolver", "content_type").order_by(
            "-created_at"
        )

        if status:
            queryset = queryset.filter(status=status)

        return list(queryset)


class WalletService:
    """Service for managing wallets and coin transactions."""

    @staticmethod
    def charge(
        user: User,
        amount: int,
        payment_key: str = "",
        order_id: str = "",
        description: str = "",
    ) -> dict:
        """
        Charge coins to user's wallet.

        Creates wallet if it doesn't exist.
        Verifies payment if payment_key and order_id are provided.

        Args:
            user instance
            amount: Amount to charge (must be positive)
            payment_key: Payment reference key (optional)
            order_id: Order ID (optional)
            description: Optional description

        Returns:
            Dict with 'wallet' and 'transaction' keys

        Raises:
            ValueError: If amount is not positive
            PaymentFailedException: If payment confirmation fails
        """
        from django.db import transaction

        from apps.interactions.models import CoinTransaction, TransactionType, Wallet

        if amount <= 0:
            raise ValueError("충전 금액은 0보다 커야 합니다")

        # Track whether payment was successfully confirmed
        # Only set to True AFTER confirm_payment succeeds
        payment_confirmed = False

        # Confirm payment if details provided (OUTSIDE try block)
        # PaymentFailedException will propagate up without triggering cancel
        if payment_key and order_id:
            PaymentService().confirm_payment(
                payment_key=payment_key,
                order_id=order_id,
                amount=amount,
            )
            payment_confirmed = True

        try:
            with transaction.atomic():
                # Get or create wallet with lock
                wallet, created = Wallet.objects.select_for_update().get_or_create(
                    user=user,
                    defaults={"balance": 0},
                )

                # Update balance
                wallet.balance += amount
                wallet.save()

                # Create transaction record
                tx = CoinTransaction.objects.create(
                    wallet=wallet,
                    transaction_type=TransactionType.CHARGE,
                    amount=amount,
                    balance_after=wallet.balance,
                    description=description,
                    reference_type="payment" if payment_key else "",
                    reference_id=None,  # storing key in description or separate field might be better but strictly following schema
                )

                # If we want to store payment info, we might need fields in CoinTransaction
                # For now, let's append to description if provided
                if payment_key:
                    tx.description = (
                        f"{description} (Payment: {payment_key})"
                        if description
                        else f"Payment: {payment_key}"
                    )
                    tx.save()
        except (IntegrityError, DatabaseError, ValueError) as e:
            # Only cancel payment if it was successfully confirmed
            # This prevents trying to cancel a payment that was never approved
            if payment_confirmed:
                PaymentService().cancel_payment(payment_key, "System Error: Transaction failed")
            raise e

        return {"wallet": wallet, "transaction": tx}

    @staticmethod
    def spend(
        user: User,
        amount: int,
        description: str = "",
        reference_type: str = "",
        reference_id: int = None,
    ) -> dict:
        """
        Spend coins from user's wallet.

        Args:
            user instance
            amount: Amount to spend (must be positive)
            description: Optional description
            reference_type: Type of related entity (e.g., 'chapter')
            reference_id: ID of related entity

        Returns:
            Dict with 'wallet' and 'transaction' keys

        Raises:
            ValueError: If amount is not positive, wallet doesn't exist,
                       or insufficient balance
        """
        from django.db import transaction

        from apps.interactions.models import CoinTransaction, TransactionType, Wallet

        if amount <= 0:
            raise ValueError("사용 금액은 0보다 커야 합니다")

        with transaction.atomic():
            try:
                wallet = Wallet.objects.select_for_update().get(user=user)
            except Wallet.DoesNotExist as e:
                raise ValueError("지갑이 존재하지 않습니다") from e

            if wallet.balance < amount:
                raise ValueError("잔액이 부족합니다")

            # Update balance
            wallet.balance -= amount
            wallet.save()

            # Create transaction record
            tx = CoinTransaction.objects.create(
                wallet=wallet,
                transaction_type=TransactionType.SPEND,
                amount=amount,
                balance_after=wallet.balance,
                description=description,
                reference_type=reference_type,
                reference_id=reference_id,
            )

        return {"wallet": wallet, "transaction": tx}

    @staticmethod
    def refund(
        user: User,
        amount: int,
        description: str = "",
        reference_type: str = "",
        reference_id: int = None,
    ) -> dict:
        """
        Refund coins to user's wallet.

        Args:
            user instance
            amount: Amount to refund (must be positive)
            description: Optional description
            reference_type: Type of related entity
            reference_id: ID of related entity

        Returns:
            Dict with 'wallet' and 'transaction' keys

        Raises:
            ValueError: If amount is not positive or wallet doesn't exist
        """
        from django.db import transaction

        from apps.interactions.models import CoinTransaction, TransactionType, Wallet

        if amount <= 0:
            raise ValueError("환불 금액은 0보다 커야 합니다")

        with transaction.atomic():
            try:
                wallet = Wallet.objects.select_for_update().get(user=user)
            except Wallet.DoesNotExist as e:
                raise ValueError("지갑이 존재하지 않습니다") from e

            # Update balance
            wallet.balance += amount
            wallet.save()

            # Create transaction record
            tx = CoinTransaction.objects.create(
                wallet=wallet,
                transaction_type=TransactionType.REFUND,
                amount=amount,
                balance_after=wallet.balance,
                description=description,
                reference_type=reference_type,
                reference_id=reference_id,
            )

        return {"wallet": wallet, "transaction": tx}

    @staticmethod
    def adjustment(
        user: User,
        amount: int,
        description: str = "",
    ) -> dict:
        """
        Adjust wallet balance (admin operation).

        Can be positive or negative. Allows balance to go below zero.

        Args:
            user instance
            amount: Amount to adjust (can be negative)
            description: Required description for audit

        Returns:
            Dict with 'wallet' and 'transaction' keys
        """
        from django.db import transaction

        from apps.interactions.models import CoinTransaction, TransactionType, Wallet

        with transaction.atomic():
            wallet, created = Wallet.objects.select_for_update().get_or_create(
                user=user,
                defaults={"balance": 0},
            )

            # Update balance (can go negative)
            wallet.balance += amount
            wallet.save()

            # Create transaction record
            tx = CoinTransaction.objects.create(
                wallet=wallet,
                transaction_type=TransactionType.ADJUSTMENT,
                amount=amount,
                balance_after=wallet.balance,
                description=description,
            )

        return {"wallet": wallet, "transaction": tx}

    @staticmethod
    def get_balance(user: User) -> int:
        """
        Get current wallet balance.

        Args:
            user instance

        Returns:
            Current balance, or 0 if no wallet
        """
        from apps.interactions.models import Wallet

        try:
            wallet = Wallet.objects.get(user=user)
            return wallet.balance
        except Wallet.DoesNotExist:
            return 0

    @staticmethod
    def get_transactions(user: User, limit: int = 20) -> list:
        """
        Get recent transactions for user.

        Args:
            user instance
            limit: Maximum number of transactions

        Returns:
            List of CoinTransaction instances
        """
        from apps.interactions.models import CoinTransaction, Wallet

        try:
            wallet = Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            return []

        return list(CoinTransaction.objects.filter(wallet=wallet).order_by("-created_at")[:limit])


class AIUsageService:
    """Service for tracking AI usage and enforcing daily limits."""

    # Tier-based daily limits per action type
    TIER_LIMITS = {
        "FREE": 5,
        "BASIC": 10,
        "PREMIUM": 20,
    }

    def increment(
        self,
        user: User,
        action_type: str,
        token_count: int = 0,
    ) -> "AIUsageLog":
        """
        Record an AI usage event.

        Creates or updates the usage log for today.

        Args:
            user instance
            action_type: AIActionType value
            token_count: Optional token count to add

        Returns:
            Updated AIUsageLog instance
        """
        from datetime import date

        from apps.interactions.models import AIUsageLog

        today = date.today()

        log, created = AIUsageLog.objects.update_or_create(
            user=user,
            usage_date=today,
            action_type=action_type,
            defaults={
                "request_count": 1,
                "token_count": token_count,
            }
            if not AIUsageLog.objects.filter(
                user=user, usage_date=today, action_type=action_type
            ).exists()
            else {},
        )

        if not created:
            # Increment existing counts
            log.request_count += 1
            log.token_count += token_count
            log.save()

        return log

    def get_daily_usage(
        self,
        user: User,
        action_type: str = None,
    ) -> int:
        """
        Get today's usage count for a user.

        Args:
            user instance
            action_type: Optional AIActionType to filter by.
                        If None, returns total across all action types.

        Returns:
            Number of requests today
        """
        from datetime import date

        from django.db.models import Sum

        from apps.interactions.models import AIUsageLog

        today = date.today()

        queryset = AIUsageLog.objects.filter(user=user, usage_date=today)

        if action_type:
            queryset = queryset.filter(action_type=action_type)

        result = queryset.aggregate(total=Sum("request_count"))
        return result["total"] or 0

    def can_use_ai(
        self,
        user: User,
        action_type: str,
    ) -> bool:
        """
        Check if user can make an AI request.

        Compares current usage against tier-based daily limit.

        Args:
            user instance
            action_type: AIActionType value

        Returns:
            True if under limit, False if at/over limit
        """
        current_usage = self.get_daily_usage(user, action_type)
        limit = self.get_daily_limit(user)

        return current_usage < limit

    def get_user_tier(self, user: User) -> str:
        """
        Get user's current subscription tier.

        Args:
            user instance

        Returns:
            "FREE", "BASIC", or "PREMIUM"
        """
        from django.utils import timezone

        from apps.interactions.models import Subscription, SubscriptionStatus

        now = timezone.now()

        # Find active subscription that hasn't expired
        subscription = (
            Subscription.objects.filter(
                user=user,
                expires_at__gt=now,
            )
            .exclude(
                status=SubscriptionStatus.EXPIRED,
            )
            .first()
        )

        if subscription:
            return subscription.plan_type

        return "FREE"

    def get_daily_limit(self, user: User) -> int:
        """
        Get user's daily AI usage limit.

        Args:
            user instance

        Returns:
            Daily limit based on tier
        """
        tier = self.get_user_tier(user)
        return self.TIER_LIMITS.get(tier, self.TIER_LIMITS["FREE"])

    def get_remaining_quota(
        self,
        user: User,
        action_type: str,
    ) -> int:
        """
        Get remaining quota for today.

        Args:
            user instance
            action_type: AIActionType value

        Returns:
            Remaining requests available today
        """
        current_usage = self.get_daily_usage(user, action_type)
        limit = self.get_daily_limit(user)

        return max(0, limit - current_usage)

    def get_usage_status(self, user: User) -> dict:
        """
        Get complete usage status for a user.

        Args:
            user instance

        Returns:
            Dict with tier, limits, and usage by action type
        """
        from datetime import date

        from apps.interactions.models import AIActionType

        today = date.today()
        tier = self.get_user_tier(user)
        limit = self.get_daily_limit(user)

        # Get usage by action type
        usage_by_action = {}
        for action_type, _label in AIActionType.choices:
            count = self.get_daily_usage(user, action_type)
            usage_by_action[action_type] = {
                "used": count,
                "remaining": max(0, limit - count),
            }

        return {
            "tier": tier,
            "daily_limit": limit,
            "usage_by_action": usage_by_action,
            "date": today.isoformat(),
        }
