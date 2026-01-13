"""
Serializers for contents app.

Contains serializers for:
- Chapter: Create, Detail, List, Update, Schedule
"""

from rest_framework import serializers

from .models import Chapter, ChapterStatus, AccessType


# =============================================================================
# Chapter Serializers
# =============================================================================


class ChapterCreateSerializer(serializers.Serializer):
    """Serializer for creating a new chapter."""

    title = serializers.CharField(max_length=200)
    content = serializers.CharField()
    access_type = serializers.ChoiceField(
        choices=AccessType.choices, required=False, default=AccessType.FREE
    )
    price = serializers.IntegerField(required=False, default=0)


class ChapterNavSerializer(serializers.Serializer):
    """Minimal serializer for prev/next navigation."""

    chapter_number = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)


class ChapterDetailSerializer(serializers.ModelSerializer):
    """Serializer for chapter detail view."""

    prev_chapter = serializers.SerializerMethodField()
    next_chapter = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = [
            "id",
            "chapter_number",
            "title",
            "content_html",
            "word_count",
            "status",
            "access_type",
            "price",
            "scheduled_at",
            "published_at",
            "view_count",
            "like_count",
            "comment_count",
            "created_at",
            "updated_at",
            "prev_chapter",
            "next_chapter",
        ]
        read_only_fields = fields

    def get_prev_chapter(self, obj):
        """Get previous chapter navigation info."""
        prev_chapter = (
            Chapter.objects.filter(
                branch_id=obj.branch_id,
                chapter_number__lt=obj.chapter_number,
                status=ChapterStatus.PUBLISHED,
            )
            .order_by("-chapter_number")
            .first()
        )
        if prev_chapter:
            return ChapterNavSerializer(prev_chapter).data
        return None

    def get_next_chapter(self, obj):
        """Get next chapter navigation info."""
        next_chapter = (
            Chapter.objects.filter(
                branch_id=obj.branch_id,
                chapter_number__gt=obj.chapter_number,
                status=ChapterStatus.PUBLISHED,
            )
            .order_by("chapter_number")
            .first()
        )
        if next_chapter:
            return ChapterNavSerializer(next_chapter).data
        return None


class ChapterListSerializer(serializers.ModelSerializer):
    """Serializer for chapter list view (summary)."""

    class Meta:
        model = Chapter
        fields = [
            "id",
            "chapter_number",
            "title",
            "word_count",
            "status",
            "access_type",
            "price",
            "scheduled_at",
            "published_at",
            "view_count",
            "like_count",
            "comment_count",
            "created_at",
        ]
        read_only_fields = fields


class ChapterUpdateSerializer(serializers.Serializer):
    """Serializer for updating a chapter (partial)."""

    title = serializers.CharField(max_length=200, required=False)
    content = serializers.CharField(required=False)
    access_type = serializers.ChoiceField(choices=AccessType.choices, required=False)
    price = serializers.IntegerField(required=False)


class ChapterScheduleSerializer(serializers.Serializer):
    """Serializer for scheduling a chapter."""

    scheduled_at = serializers.DateTimeField()
