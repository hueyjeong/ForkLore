"""
Serializers for interactions app.

Contains serializers for:
- Subscription: Create, Detail, Status
- Purchase: Create, Detail, List
"""

from rest_framework import serializers

from apps.contents.serializers import ChapterListSerializer

from .models import (
    Bookmark,
    Comment,
    PlanType,
    Purchase,
    ReadingLog,
    Report,
    ReportReason,
    Subscription,
)

# =============================================================================
# Subscription Serializers
# =============================================================================


class SubscriptionCreateSerializer(serializers.Serializer):
    """Serializer for creating a subscription."""

    plan_type = serializers.ChoiceField(choices=PlanType.choices, default=PlanType.BASIC)
    days = serializers.IntegerField(min_value=1, default=30)
    payment_id = serializers.CharField(required=False, allow_blank=True, default="")
    order_id = serializers.CharField(required=False, allow_blank=True, default="")


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


# =============================================================================
# ReadingLog Serializers
# =============================================================================


class ReadingProgressSerializer(serializers.Serializer):
    """Serializer for recording reading progress."""

    progress = serializers.DecimalField(max_digits=5, decimal_places=4, min_value=0, max_value=1)


class ReadingLogSerializer(serializers.ModelSerializer):
    """Serializer for reading log."""

    chapter = ChapterListSerializer(read_only=True)

    class Meta:
        model = ReadingLog
        fields = [
            "id",
            "chapter",
            "progress",
            "is_completed",
            "read_at",
        ]
        read_only_fields = fields


class ContinueReadingSerializer(serializers.Serializer):
    """Serializer for continue reading response."""

    chapter = ChapterListSerializer(read_only=True, allow_null=True)
    progress = serializers.DecimalField(max_digits=5, decimal_places=4, read_only=True)


# =============================================================================
# Bookmark Serializers
# =============================================================================


class BookmarkCreateSerializer(serializers.Serializer):
    """Serializer for creating a bookmark."""

    scroll_position = serializers.DecimalField(
        max_digits=5, decimal_places=4, min_value=0, max_value=1, default=0
    )
    note = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")


class BookmarkSerializer(serializers.ModelSerializer):
    """Serializer for bookmark."""

    chapter = ChapterListSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = [
            "id",
            "chapter",
            "scroll_position",
            "note",
            "created_at",
        ]
        read_only_fields = fields


# =============================================================================
# Comment Serializers
# =============================================================================


class UserBriefSerializer(serializers.Serializer):
    """Brief user info for comments."""

    id = serializers.IntegerField(read_only=True)
    nickname = serializers.CharField(read_only=True)
    profile_image = serializers.CharField(read_only=True, allow_null=True)


class CommentCreateSerializer(serializers.Serializer):
    """Serializer for creating a comment."""

    content = serializers.CharField(max_length=5000)
    is_spoiler = serializers.BooleanField(default=False)
    parent_id = serializers.IntegerField(required=False, allow_null=True)
    paragraph_index = serializers.IntegerField(required=False, allow_null=True)
    selection_start = serializers.IntegerField(required=False, allow_null=True)
    selection_end = serializers.IntegerField(required=False, allow_null=True)
    quoted_text = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, data: dict) -> dict:
        start = data.get("selection_start")
        end = data.get("selection_end")
        if start is not None and end is not None and start >= end:
            raise serializers.ValidationError("selection_start must be less than selection_end")
        return data


class CommentUpdateSerializer(serializers.Serializer):
    """Serializer for updating a comment."""

    content = serializers.CharField(max_length=5000, required=False)
    is_spoiler = serializers.BooleanField(required=False)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comment."""

    user = UserBriefSerializer(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "content",
            "is_spoiler",
            "is_pinned",
            "like_count",
            "paragraph_index",
            "selection_start",
            "selection_end",
            "quoted_text",
            "parent_id",
            "reply_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


# =============================================================================
# Like Serializers
# =============================================================================


class LikeToggleResponseSerializer(serializers.Serializer):
    """Serializer for like toggle response."""

    liked = serializers.BooleanField(read_only=True)
    like_count = serializers.IntegerField(read_only=True, allow_null=True)


# =============================================================================
# Report Serializers
# =============================================================================

REPORT_TARGET_TYPES = {
    "comment": "interactions.Comment",
    "chapter": "contents.Chapter",
    "novel": "novels.Novel",
    "branch": "novels.Branch",
}


class ReportCreateSerializer(serializers.Serializer):
    """Serializer for creating a report."""

    target_type = serializers.ChoiceField(choices=list(REPORT_TARGET_TYPES.keys()))
    target_id = serializers.IntegerField()
    reason = serializers.ChoiceField(choices=ReportReason.choices)
    description = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, data: dict) -> dict:
        """Validate that the target exists."""
        from django.apps import apps
        from django.core.exceptions import ObjectDoesNotExist

        target_type = data["target_type"]
        target_id = data["target_id"]

        model_path = REPORT_TARGET_TYPES[target_type]
        app_label, model_name = model_path.rsplit(".", 1)

        try:
            model = apps.get_model(app_label, model_name)
            target = model.objects.get(id=target_id)
            data["target"] = target
        except ObjectDoesNotExist as e:
            raise serializers.ValidationError({"target_id": "대상을 찾을 수 없습니다."}) from e

        return data


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for report list/detail."""

    reporter = UserBriefSerializer(read_only=True)
    target_type = serializers.SerializerMethodField()
    target_id = serializers.IntegerField(source="object_id", read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "reporter",
            "target_type",
            "target_id",
            "reason",
            "description",
            "status",
            "created_at",
        ]
        read_only_fields = fields

    def get_target_type(self, obj: Report) -> str:
        """Get human-readable target type."""
        model_name = obj.content_type.model
        return model_name


class ReportAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin report detail with resolution fields."""

    reporter = UserBriefSerializer(read_only=True)
    resolver = UserBriefSerializer(read_only=True, allow_null=True)
    target_type = serializers.SerializerMethodField()
    target_id = serializers.IntegerField(source="object_id", read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "reporter",
            "target_type",
            "target_id",
            "reason",
            "description",
            "status",
            "resolver",
            "resolved_at",
            "resolution_note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_target_type(self, obj: Report) -> str:
        """Get human-readable target type."""
        return obj.content_type.model


class ReportActionSerializer(serializers.Serializer):
    """Serializer for admin report actions."""

    action = serializers.ChoiceField(choices=["resolve", "reject"])
    resolution_note = serializers.CharField(required=False, allow_blank=True, default="")


# =============================================================================
# Wallet Serializers
# =============================================================================


class WalletChargeSerializer(serializers.Serializer):
    """Serializer for charging coins."""

    amount = serializers.IntegerField(min_value=1)
    description = serializers.CharField(required=False, allow_blank=True, default="")


class WalletAdjustmentSerializer(serializers.Serializer):
    """Serializer for admin wallet adjustment."""

    amount = serializers.IntegerField()  # Can be negative
    description = serializers.CharField(required=False, allow_blank=True, default="")


class CoinTransactionSerializer(serializers.Serializer):
    """Serializer for coin transaction."""

    id = serializers.IntegerField(read_only=True)
    transaction_type = serializers.CharField(read_only=True)
    amount = serializers.IntegerField(read_only=True)
    balance_after = serializers.IntegerField(read_only=True)
    description = serializers.CharField(read_only=True)
    reference_type = serializers.CharField(read_only=True)
    reference_id = serializers.IntegerField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)


class WalletSerializer(serializers.Serializer):
    """Serializer for wallet with recent transactions."""

    balance = serializers.IntegerField(read_only=True)
    recent_transactions = CoinTransactionSerializer(many=True, read_only=True)


class WalletBalanceResponseSerializer(serializers.Serializer):
    """Serializer for wallet balance response after charge/adjustment."""

    balance = serializers.IntegerField(read_only=True)
    transaction = CoinTransactionSerializer(read_only=True)


# =============================================================================
# AI Usage Serializers
# =============================================================================


class AIUsageActionTypeField(serializers.ChoiceField):
    """Custom field for AI action type validation."""

    def __init__(self, **kwargs: object) -> None:
        from apps.interactions.models import AIActionType

        super().__init__(choices=AIActionType.choices, **kwargs)


class AIUsageCheckLimitSerializer(serializers.Serializer):
    """Serializer for checking AI usage limit."""

    action_type = AIUsageActionTypeField()
    enforce = serializers.BooleanField(default=False)


class AIUsageCheckLimitResponseSerializer(serializers.Serializer):
    """Response for check limit endpoint."""

    allowed = serializers.BooleanField(read_only=True)
    remaining = serializers.IntegerField(read_only=True)
    daily_limit = serializers.IntegerField(read_only=True)
    tier = serializers.CharField(read_only=True)


class AIUsageRecordSerializer(serializers.Serializer):
    """Serializer for recording AI usage."""

    action_type = AIUsageActionTypeField()
    token_count = serializers.IntegerField(required=False, default=0, min_value=0)


class AIUsageRecordResponseSerializer(serializers.Serializer):
    """Response for record usage endpoint."""

    used = serializers.IntegerField(read_only=True)
    remaining = serializers.IntegerField(read_only=True)
    daily_limit = serializers.IntegerField(read_only=True)


class AIUsageByActionSerializer(serializers.Serializer):
    """Usage info for a single action type."""

    used = serializers.IntegerField(read_only=True)
    remaining = serializers.IntegerField(read_only=True)


class AIUsageStatusSerializer(serializers.Serializer):
    """Serializer for AI usage status response."""

    tier = serializers.CharField(read_only=True)
    daily_limit = serializers.IntegerField(read_only=True)
    usage_by_action = serializers.DictField(
        child=AIUsageByActionSerializer(),
        read_only=True,
    )
    date = serializers.CharField(read_only=True)
