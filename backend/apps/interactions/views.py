"""
ViewSets for interactions app.

Contains views for:
- SubscriptionViewSet: Subscribe, cancel, status
- PurchaseViewSet: Purchase chapter, list purchases
- CommentViewSet: Comment CRUD, pin/unpin
- LikeViewSet: Like toggle
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.contents.models import Chapter
from common.pagination import StandardPagination

from .models import Comment, Report
from .serializers import (
    CoinTransactionSerializer,
    CommentCreateSerializer,
    CommentSerializer,
    CommentUpdateSerializer,
    LikeToggleResponseSerializer,
    PurchaseDetailSerializer,
    PurchaseListSerializer,
    ReportActionSerializer,
    ReportAdminSerializer,
    ReportCreateSerializer,
    ReportSerializer,
    SubscriptionCreateSerializer,
    SubscriptionDetailSerializer,
    SubscriptionStatusSerializer,
    WalletAdjustmentSerializer,
    WalletChargeSerializer,
)
from .services import (
    CommentService,
    LikeService,
    PurchaseService,
    ReportService,
    SubscriptionService,
    WalletService,
)


@extend_schema_view(
    create=extend_schema(
        summary="구독 가입",
        description="새 구독을 생성하거나 기존 구독을 연장합니다.",
        tags=["Subscriptions"],
    ),
)
class SubscriptionViewSet(viewsets.ViewSet):
    """
    ViewSet for subscription management.

    Routes:
    - POST /subscriptions/ - Subscribe
    - DELETE /subscriptions/current/ - Cancel subscription
    - GET /users/me/subscription/ - Get subscription status (via users app)
    """

    permission_classes = [IsAuthenticated]

    def create(self, request: Request) -> Response:
        """Create or extend subscription."""
        serializer = SubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = SubscriptionService()
        subscription = service.subscribe(
            user=request.user,
            plan_type=serializer.validated_data.get("plan_type", "BASIC"),
            days=serializer.validated_data.get("days", 30),
            payment_id=serializer.validated_data.get("payment_id", ""),
            order_id=serializer.validated_data.get("order_id", ""),
        )

        response_serializer = SubscriptionDetailSerializer(subscription)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="구독 취소",
        description="현재 구독을 취소합니다. 만료일까지는 이용 가능합니다.",
        tags=["Subscriptions"],
    )
    @action(detail=False, methods=["delete"], url_path="current")
    def cancel_current(self, request: Request) -> Response:
        """Cancel current subscription."""
        service = SubscriptionService()
        result = service.cancel(user=request.user)

        if not result:
            raise NotFound("활성 구독이 없습니다.")

        return Response({"message": "구독이 취소되었습니다."}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="구독 상태 조회",
        description="현재 구독 상태를 조회합니다.",
        tags=["Subscriptions"],
    )
    @action(detail=False, methods=["get"], url_path="status")
    def subscription_status(self, request: Request) -> Response:
        """Get subscription status."""
        service = SubscriptionService()
        result = service.get_status(user=request.user)

        if not result:
            return Response(None)

        serializer = SubscriptionStatusSerializer(result)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="소장 목록 조회",
        description="내가 소장한 회차 목록을 조회합니다.",
        tags=["Purchases"],
    ),
)
class PurchaseViewSet(viewsets.ViewSet):
    """
    ViewSet for chapter purchases.

    Routes:
    - GET /purchases/ - List my purchases
    - POST /chapters/{id}/purchase/ - Purchase a chapter (via contents app)
    """

    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def list(self, request: Request) -> Response:
        """List user's purchases."""
        service = PurchaseService()
        purchases = service.get_purchase_list(user=request.user)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(purchases, request)
        serializer = PurchaseListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


class ChapterPurchaseViewSet(viewsets.ViewSet):
    """
    ViewSet for purchasing individual chapters.

    Routes:
    - POST /chapters/{id}/purchase/ - Purchase a chapter
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="회차 소장",
        description="회차를 소장 구매합니다.",
        tags=["Purchases"],
    )
    def create(self, request: Request, chapter_pk: int | None = None) -> Response:
        """Purchase a chapter."""
        try:
            chapter = Chapter.objects.get(pk=chapter_pk)
        except Chapter.DoesNotExist as e:
            raise NotFound("회차를 찾을 수 없습니다.") from e

        service = PurchaseService()
        try:
            purchase = service.purchase(user=request.user, chapter=chapter)
        except ValueError as e:
            raise ValidationError(str(e)) from e

        serializer = PurchaseDetailSerializer(purchase)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# =============================================================================
# Comment ViewSets
# =============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="댓글 목록 조회",
        description="회차의 댓글 목록을 조회합니다.",
        tags=["Comments"],
    ),
    create=extend_schema(
        summary="댓글 작성",
        description="새 댓글을 작성합니다.",
        tags=["Comments"],
    ),
)
class ChapterCommentViewSet(viewsets.ViewSet):
    """
    ViewSet for comments nested under chapters.

    Routes:
    - GET /chapters/{chapter_pk}/comments/ - List comments
    - POST /chapters/{chapter_pk}/comments/ - Create comment
    """

    pagination_class = StandardPagination

    def get_permissions(self) -> list:
        if self.action == "create":
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request: Request, chapter_pk: int | None = None) -> Response:
        """List comments for a chapter."""
        paragraph_index = request.query_params.get("paragraph_index")
        paragraph_index = int(paragraph_index) if paragraph_index else None

        comments = CommentService.list(
            chapter_id=chapter_pk,
            paragraph_index=paragraph_index,
        )

        paginator = StandardPagination()
        page = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def create(self, request: Request, chapter_pk: int | None = None) -> Response:
        """Create a new comment."""
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            comment = CommentService.create(
                user=request.user,
                chapter_id=chapter_pk,
                **serializer.validated_data,
            )
        except Exception as e:
            raise ValidationError(str(e)) from e

        response_serializer = CommentSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    partial_update=extend_schema(
        summary="댓글 수정",
        description="댓글을 수정합니다.",
        tags=["Comments"],
    ),
    destroy=extend_schema(
        summary="댓글 삭제",
        description="댓글을 삭제합니다.",
        tags=["Comments"],
    ),
)
class CommentDetailViewSet(viewsets.ViewSet):
    """
    ViewSet for comment operations by ID.

    Routes:
    - PATCH /comments/{id}/ - Update comment
    - DELETE /comments/{id}/ - Delete comment
    - POST /comments/{id}/pin/ - Pin comment
    - DELETE /comments/{id}/pin/ - Unpin comment
    - POST /comments/{id}/like/ - Like comment
    - DELETE /comments/{id}/like/ - Unlike comment
    """

    permission_classes = [IsAuthenticated]

    def partial_update(self, request: Request, pk: int | None = None) -> Response:
        """Update a comment."""
        serializer = CommentUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            comment = CommentService.update(
                comment_id=pk,
                user=request.user,
                **serializer.validated_data,
            )
        except PermissionError as e:
            raise PermissionDenied(str(e)) from e
        except Comment.DoesNotExist as e:
            raise NotFound("댓글을 찾을 수 없습니다.") from e

        response_serializer = CommentSerializer(comment)
        return Response(response_serializer.data)

    def destroy(self, request: Request, pk: int | None = None) -> Response:
        """Delete a comment."""
        try:
            CommentService.delete(comment_id=pk, user=request.user)
        except PermissionError as e:
            raise PermissionDenied(str(e)) from e
        except Comment.DoesNotExist as e:
            raise NotFound("댓글을 찾을 수 없습니다.") from e

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="댓글 고정",
        description="작가가 댓글을 고정합니다.",
        tags=["Comments"],
    )
    @action(detail=True, methods=["post", "delete"])
    def pin(self, request: Request, pk: int | None = None) -> Response:
        """Pin or unpin a comment."""
        try:
            if request.method == "POST":
                comment = CommentService.pin(comment_id=pk, user=request.user)
            else:
                comment = CommentService.unpin(comment_id=pk, user=request.user)
        except PermissionError as e:
            raise PermissionDenied(str(e)) from e
        except Comment.DoesNotExist as e:
            raise NotFound("댓글을 찾을 수 없습니다.") from e

        response_serializer = CommentSerializer(comment)
        return Response(response_serializer.data)

    @extend_schema(
        summary="댓글 좋아요",
        description="댓글에 좋아요를 누르거나 취소합니다.",
        tags=["Comments"],
    )
    @action(detail=True, methods=["post", "delete"])
    def like(self, request: Request, pk: int | None = None) -> Response:
        """Like or unlike a comment."""
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist as e:
            raise NotFound("댓글을 찾을 수 없습니다.") from e

        result = LikeService.toggle(user=request.user, target=comment)
        serializer = LikeToggleResponseSerializer(result)
        return Response(serializer.data)


class ChapterLikeViewSet(viewsets.ViewSet):
    """
    ViewSet for chapter likes.

    Routes:
    - POST /chapters/{chapter_pk}/like/ - Like chapter
    - DELETE /chapters/{chapter_pk}/like/ - Unlike chapter
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="회차 좋아요",
        description="회차에 좋아요를 누르거나 취소합니다.",
        tags=["Chapters"],
    )
    def create(self, request: Request, chapter_pk: int | None = None) -> Response:
        """Like or unlike a chapter."""
        try:
            chapter = Chapter.objects.get(pk=chapter_pk)
        except Chapter.DoesNotExist as e:
            raise NotFound("회차를 찾을 수 없습니다.") from e

        result = LikeService.toggle(user=request.user, target=chapter)
        serializer = LikeToggleResponseSerializer(result)
        return Response(serializer.data)


# =============================================================================
# Report ViewSets
# =============================================================================


@extend_schema_view(
    create=extend_schema(
        summary="신고 생성",
        description="콘텐츠를 신고합니다.",
        tags=["Reports"],
    ),
)
class ReportViewSet(viewsets.ViewSet):
    """
    ViewSet for creating reports (authenticated users).

    Routes:
    - POST /reports/ - Create a report
    """

    permission_classes = [IsAuthenticated]

    def create(self, request: Request) -> Response:
        """Create a new report."""
        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target = serializer.validated_data["target"]

        try:
            report = ReportService.create_report(
                reporter=request.user,
                target=target,
                reason=serializer.validated_data["reason"],
                description=serializer.validated_data.get("description", ""),
            )
        except ValueError as e:
            raise ValidationError(str(e)) from e

        response_serializer = ReportSerializer(report)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(
        summary="신고 목록 조회 (관리자)",
        description="모든 신고 목록을 조회합니다.",
        tags=["Admin - Reports"],
    ),
    partial_update=extend_schema(
        summary="신고 처리 (관리자)",
        description="신고를 처리(승인/반려)합니다.",
        tags=["Admin - Reports"],
    ),
)
class AdminReportViewSet(viewsets.ViewSet):
    """
    ViewSet for admin report management.

    Routes:
    - GET /admin/reports/ - List all reports
    - PATCH /admin/reports/{id}/ - Process a report
    """

    permission_classes = [IsAdminUser]
    pagination_class = StandardPagination

    def list(self, request: Request) -> Response:
        """List all reports."""
        status_filter = request.query_params.get("status")

        if status_filter:
            reports = ReportService.list_all(status=status_filter)
        else:
            reports = ReportService.list_all()

        paginator = StandardPagination()
        page = paginator.paginate_queryset(reports, request)
        serializer = ReportAdminSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def partial_update(self, request: Request, pk: int | None = None) -> Response:
        """Process a report (resolve/reject)."""
        serializer = ReportActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_type = serializer.validated_data["action"]
        note = serializer.validated_data.get("resolution_note", "")

        try:
            if action_type == "resolve":
                report = ReportService.admin_resolve(
                    report_id=pk,
                    resolver=request.user,
                    note=note,
                )
            else:  # reject
                report = ReportService.admin_reject(
                    report_id=pk,
                    resolver=request.user,
                    note=note,
                )
        except Report.DoesNotExist as e:
            raise NotFound("신고를 찾을 수 없습니다.") from e
        except PermissionError as e:
            raise PermissionDenied(str(e)) from e
        except ValueError as e:
            raise ValidationError(str(e)) from e

        response_serializer = ReportAdminSerializer(report)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


# =============================================================================
# Wallet ViewSets
# =============================================================================


@extend_schema_view(
    create=extend_schema(
        summary="코인 충전",
        description="코인을 충전합니다 (MVP: 내부 시뮬레이션).",
        tags=["Wallet"],
    ),
)
class WalletChargeViewSet(viewsets.ViewSet):
    """
    ViewSet for charging coins.

    Routes:
    - POST /wallet/charge/ - Charge coins
    """

    permission_classes = [IsAuthenticated]

    def create(self, request: Request) -> Response:
        """Charge coins to user's wallet."""
        serializer = WalletChargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = WalletService.charge(
                user=request.user,
                amount=serializer.validated_data["amount"],
                description=serializer.validated_data.get("description", ""),
            )
        except ValueError as e:
            raise ValidationError(str(e)) from e

        return Response(
            {
                "balance": result["wallet"].balance,
                "transaction": CoinTransactionSerializer(result["transaction"]).data,
            },
            status=status.HTTP_201_CREATED,
        )


class UserWalletViewSet(viewsets.ViewSet):
    """
    ViewSet for user wallet operations.

    Routes:
    - GET /users/me/wallet/ - Get balance and recent transactions
    - GET /users/me/wallet/transactions/ - Get full transaction history
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="지갑 조회",
        description="잔액과 최근 거래 내역을 조회합니다.",
        tags=["Wallet"],
    )
    def retrieve(self, request: Request) -> Response:
        """Get wallet balance and recent transactions."""
        balance = WalletService.get_balance(user=request.user)
        transactions = WalletService.get_transactions(user=request.user, limit=5)

        return Response(
            {
                "balance": balance,
                "recentTransactions": CoinTransactionSerializer(transactions, many=True).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="거래 내역 조회",
        description="전체 거래 내역을 조회합니다.",
        tags=["Wallet"],
    )
    @action(detail=False, methods=["get"], url_path="transactions")
    def transactions(self, request: Request) -> Response:
        """Get full transaction history with pagination."""
        from apps.interactions.models import CoinTransaction, Wallet

        try:
            wallet = Wallet.objects.get(user=request.user)
            transactions = CoinTransaction.objects.filter(wallet=wallet).order_by("-created_at")
        except Wallet.DoesNotExist:
            transactions = []

        paginator = StandardPagination()
        page = paginator.paginate_queryset(list(transactions), request)
        serializer = CoinTransactionSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


@extend_schema_view(
    create=extend_schema(
        summary="지갑 조정 (관리자)",
        description="관리자가 사용자의 지갑 잔액을 조정합니다.",
        tags=["Admin - Wallet"],
    ),
)
class AdminWalletAdjustmentViewSet(viewsets.ViewSet):
    """
    ViewSet for admin wallet adjustments.

    Routes:
    - POST /admin/wallet/{user_id}/adjustment/ - Adjust wallet balance
    """

    permission_classes = [IsAdminUser]

    def create(self, request: Request, user_pk: int | None = None) -> Response:
        """Adjust user's wallet balance."""
        from apps.users.models import User

        try:
            target_user = User.objects.get(pk=user_pk)
        except User.DoesNotExist as e:
            raise NotFound("사용자를 찾을 수 없습니다.") from e

        serializer = WalletAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = WalletService.adjustment(
            user=target_user,
            amount=serializer.validated_data["amount"],
            description=serializer.validated_data.get("description", ""),
        )

        return Response(
            {
                "balance": result["wallet"].balance,
                "transaction": CoinTransactionSerializer(result["transaction"]).data,
            },
            status=status.HTTP_200_OK,
        )


# =============================================================================
# AI Usage ViewSets
# =============================================================================


@extend_schema_view(
    usage_status=extend_schema(
        summary="AI 사용량 조회",
        description="현재 사용자의 AI 사용량과 한도를 조회합니다.",
        tags=["AI Usage"],
    ),
)
class UserAIUsageViewSet(viewsets.ViewSet):
    """
    ViewSet for user AI usage.

    Routes:
    - GET /users/me/ai-usage/ - Get AI usage status
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="", url_name="usage-status")
    def usage_status(self, request: Request) -> Response:
        """Get AI usage status for current user."""
        from apps.interactions.serializers import AIUsageStatusSerializer
        from apps.interactions.services import AIUsageService

        service = AIUsageService()
        status_data = service.get_usage_status(request.user)

        serializer = AIUsageStatusSerializer(status_data)
        return Response(serializer.data)


@extend_schema_view(
    check_limit=extend_schema(
        summary="AI 한도 체크",
        description="AI 사용 가능 여부를 확인합니다.",
        tags=["AI Usage"],
    ),
    record_usage=extend_schema(
        summary="AI 사용량 기록",
        description="AI 사용량을 기록합니다.",
        tags=["AI Usage"],
    ),
)
class AIUsageViewSet(viewsets.ViewSet):
    """
    ViewSet for AI usage operations.

    Routes:
    - POST /ai/check-limit/ - Check if user can use AI
    - POST /ai/record-usage/ - Record AI usage
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="check-limit", url_name="check-limit")
    def check_limit(self, request: Request) -> Response:
        """Check if user can use AI."""
        from apps.interactions.serializers import (
            AIUsageCheckLimitSerializer,
        )
        from apps.interactions.services import AIUsageService

        serializer = AIUsageCheckLimitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = AIUsageService()
        action_type = serializer.validated_data["action_type"]
        enforce = serializer.validated_data.get("enforce", False)

        allowed = service.can_use_ai(user=request.user, action_type=action_type)
        remaining = service.get_remaining_quota(user=request.user, action_type=action_type)
        daily_limit = service.get_daily_limit(request.user)
        tier = service.get_user_tier(request.user)

        # If enforce mode and not allowed, return 429
        if enforce and not allowed:
            return Response(
                {"detail": "AI 사용 한도를 초과했습니다.", "remaining": 0, "tier": tier},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        response_data = {
            "allowed": allowed,
            "remaining": remaining,
            "daily_limit": daily_limit,
            "tier": tier,
        }

        return Response(response_data)

    @action(detail=False, methods=["post"], url_path="record-usage", url_name="record-usage")
    def record_usage(self, request: Request) -> Response:
        """Record AI usage."""
        from apps.interactions.serializers import (
            AIUsageRecordSerializer,
        )
        from apps.interactions.services import AIUsageService

        serializer = AIUsageRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = AIUsageService()
        action_type = serializer.validated_data["action_type"]
        token_count = serializer.validated_data.get("token_count", 0)

        # Check if user can use before recording
        if not service.can_use_ai(user=request.user, action_type=action_type):
            return Response(
                {"detail": "AI 사용 한도를 초과했습니다."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Record usage
        log = service.increment(
            user=request.user,
            action_type=action_type,
            token_count=token_count,
        )

        remaining = service.get_remaining_quota(user=request.user, action_type=action_type)
        daily_limit = service.get_daily_limit(request.user)

        response_data = {
            "used": log.request_count,
            "remaining": remaining,
            "daily_limit": daily_limit,
        }

        return Response(response_data)
