"""
Serializers for contents app.

Contains serializers for:
- Chapter: Create, Detail, List, Update, Schedule
- WikiEntry: Create, Detail, List, Update
- WikiTagDefinition: Create, Detail, List
- WikiSnapshot: Create, Detail, List
"""

from rest_framework import serializers

from .models import (
    Chapter,
    ChapterStatus,
    AccessType,
    WikiEntry,
    WikiSnapshot,
    WikiTagDefinition,
)


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


# =============================================================================
# Wiki Serializers
# =============================================================================


class WikiTagDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for WikiTagDefinition."""

    class Meta:
        model = WikiTagDefinition
        fields = [
            "id",
            "name",
            "color",
            "icon",
            "description",
            "display_order",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class WikiTagDefinitionCreateSerializer(serializers.Serializer):
    """Serializer for creating a tag definition."""

    name = serializers.CharField(max_length=100)
    color = serializers.CharField(max_length=7, required=False, default="")
    icon = serializers.CharField(max_length=50, required=False, default="")
    description = serializers.CharField(required=False, default="")
    display_order = serializers.IntegerField(required=False, default=0)


class WikiSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for WikiSnapshot."""

    class Meta:
        model = WikiSnapshot
        fields = [
            "id",
            "content",
            "valid_from_chapter",
            "contributor_type",
            "created_at",
        ]
        read_only_fields = fields


class WikiSnapshotCreateSerializer(serializers.Serializer):
    """Serializer for creating a snapshot."""

    content = serializers.CharField()
    valid_from_chapter = serializers.IntegerField()


class WikiEntryListSerializer(serializers.ModelSerializer):
    """Serializer for wiki list view."""

    tags = WikiTagDefinitionSerializer(many=True, read_only=True)

    class Meta:
        model = WikiEntry
        fields = [
            "id",
            "name",
            "image_url",
            "first_appearance",
            "tags",
            "created_at",
        ]
        read_only_fields = fields


class WikiEntryDetailSerializer(serializers.ModelSerializer):
    """Serializer for wiki detail view."""

    tags = WikiTagDefinitionSerializer(many=True, read_only=True)
    snapshots = WikiSnapshotSerializer(many=True, read_only=True)
    snapshot = serializers.SerializerMethodField()

    class Meta:
        model = WikiEntry
        fields = [
            "id",
            "name",
            "image_url",
            "first_appearance",
            "hidden_note",
            "ai_metadata",
            "tags",
            "snapshots",
            "snapshot",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_snapshot(self, obj):
        """Get context-aware snapshot if chapter is specified."""
        chapter = self.context.get("chapter")
        if chapter is not None:
            from .services import WikiService

            snapshot = WikiService.get_snapshot_for_chapter(obj.id, chapter)
            if snapshot:
                return WikiSnapshotSerializer(snapshot).data
        return None


class WikiEntryCreateSerializer(serializers.Serializer):
    """Serializer for creating a wiki entry."""

    name = serializers.CharField(max_length=200)
    image_url = serializers.URLField(required=False, default="")
    first_appearance = serializers.IntegerField(required=False, allow_null=True)
    hidden_note = serializers.CharField(required=False, default="")
    initial_content = serializers.CharField(required=False)


class WikiEntryUpdateSerializer(serializers.Serializer):
    """Serializer for updating a wiki entry."""

    name = serializers.CharField(max_length=200, required=False)
    image_url = serializers.URLField(required=False)
    first_appearance = serializers.IntegerField(required=False, allow_null=True)
    hidden_note = serializers.CharField(required=False)


class WikiTagUpdateSerializer(serializers.Serializer):
    """Serializer for updating wiki tags."""

    tag_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)
