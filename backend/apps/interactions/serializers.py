"""
Serializers for interactions app.

Contains serializers for:
- Subscription: Create, Detail, Status
- Purchase: Create, Detail, List
"""

from rest_framework import serializers

from apps.contents.serializers import ChapterListSerializer
from .models import Subscription, Purchase, PlanType, SubscriptionStatus


# =============================================================================
# Subscription Serializers
# =============================================================================


class SubscriptionCreateSerializer(serializers.Serializer):
    """Serializer for creating a subscription."""

    plan_type = serializers.ChoiceField(choices=PlanType.choices, default=PlanType.BASIC)
    days = serializers.IntegerField(min_value=1, default=30)
    payment_id = serializers.CharField(required=False, allow_blank=True, default="")


class SubscriptionDetailSerializer(serializers.ModelSerializer):
    """Serializer for subscription detail."""

    class Meta:
        model = Subscription
        fields = [
            "id",
            "plan_type",
            "status",
            "started_at",
            "expires_at",
            "cancelled_at",
            "auto_renew",
            "created_at",
        ]
        read_only_fields = fields


class SubscriptionStatusSerializer(serializers.Serializer):
    """Serializer for subscription status response."""

    id = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    plan_type = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    started_at = serializers.DateTimeField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)
    cancelled_at = serializers.DateTimeField(read_only=True, allow_null=True)
    auto_renew = serializers.BooleanField(read_only=True)


# =============================================================================
# Purchase Serializers
# =============================================================================


class PurchaseCreateSerializer(serializers.Serializer):
    """Serializer for purchasing a chapter (empty - chapter_id from URL)."""

    pass


class PurchaseDetailSerializer(serializers.ModelSerializer):
    """Serializer for purchase detail."""

    chapter_id = serializers.IntegerField(source="chapter.id", read_only=True)
    chapter_title = serializers.CharField(source="chapter.title", read_only=True)
    chapter_number = serializers.IntegerField(source="chapter.chapter_number", read_only=True)

    class Meta:
        model = Purchase
        fields = [
            "id",
            "chapter_id",
            "chapter_title",
            "chapter_number",
            "price_paid",
            "created_at",
        ]
        read_only_fields = fields


class PurchaseListSerializer(serializers.ModelSerializer):
    """Serializer for purchase list."""

    chapter = ChapterListSerializer(read_only=True)

    class Meta:
        model = Purchase
        fields = [
            "id",
            "chapter",
            "price_paid",
            "created_at",
        ]
        read_only_fields = fields
