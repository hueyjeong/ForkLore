"""
ViewSets for interactions app.

Contains views for:
- SubscriptionViewSet: Subscribe, cancel, status
- PurchaseViewSet: Purchase chapter, list purchases
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from common.pagination import StandardPagination

from apps.contents.models import Chapter
from .services import SubscriptionService, PurchaseService
from .serializers import (
    SubscriptionCreateSerializer,
    SubscriptionDetailSerializer,
    SubscriptionStatusSerializer,
    PurchaseDetailSerializer,
    PurchaseListSerializer,
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

    def create(self, request):
        """Create or extend subscription."""
        serializer = SubscriptionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "유효성 검사 실패", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = SubscriptionService()
        subscription = service.subscribe(
            user=request.user,
            plan_type=serializer.validated_data.get("plan_type", "BASIC"),
            days=serializer.validated_data.get("days", 30),
            payment_id=serializer.validated_data.get("payment_id", ""),
        )

        response_serializer = SubscriptionDetailSerializer(subscription)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="구독 취소",
        description="현재 구독을 취소합니다. 만료일까지는 이용 가능합니다.",
        tags=["Subscriptions"],
    )
    @action(detail=False, methods=["delete"], url_path="current")
    def cancel_current(self, request):
        """Cancel current subscription."""
        service = SubscriptionService()
        result = service.cancel(user=request.user)

        if not result:
            return Response(
                {"success": False, "message": "활성 구독이 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"success": True, "message": "구독이 취소되었습니다.", "data": None},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="구독 상태 조회",
        description="현재 구독 상태를 조회합니다.",
        tags=["Subscriptions"],
    )
    @action(detail=False, methods=["get"], url_path="status")
    def subscription_status(self, request):
        """Get subscription status."""
        service = SubscriptionService()
        result = service.get_status(user=request.user)

        if not result:
            return Response(
                {"success": True, "message": "구독 정보가 없습니다.", "data": None},
                status=status.HTTP_200_OK,
            )

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

    def list(self, request):
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
    def create(self, request, chapter_pk=None):
        """Purchase a chapter."""
        try:
            chapter = Chapter.objects.get(pk=chapter_pk)
        except Chapter.DoesNotExist:
            return Response(
                {"success": False, "message": "회차를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        service = PurchaseService()
        try:
            purchase = service.purchase(user=request.user, chapter=chapter)
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PurchaseDetailSerializer(purchase)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
