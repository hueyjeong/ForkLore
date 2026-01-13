"""
Serializers for interactions app.

Contains serializers for:
- Subscription: Create, Detail, Status
- Purchase: Create, Detail, List
"""

from rest_framework import serializers

from apps.contents.serializers import ChapterListSerializer
from .models import (
    Subscription,
    Purchase,
    PlanType,
    SubscriptionStatus,
    ReadingLog,
    Bookmark,
    Comment,
    Like,
)


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

    def validate(self, data):
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
    reply_count = serializers.SerializerMethodField()

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

    def get_reply_count(self, obj):
        return obj.replies.filter(deleted_at__isnull=True).count()


# =============================================================================
# Like Serializers
# =============================================================================


class LikeToggleResponseSerializer(serializers.Serializer):
    """Serializer for like toggle response."""

    liked = serializers.BooleanField(read_only=True)
    like_count = serializers.IntegerField(read_only=True, allow_null=True)
