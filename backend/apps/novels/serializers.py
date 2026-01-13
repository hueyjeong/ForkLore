"""
Serializers for novels app.

Contains serializers for:
- Novel: Create, Detail, List, Update
- Branch: Create, Detail, List, Update
- BranchLinkRequest: Create, Detail
"""

from rest_framework import serializers

from .models import (
    AgeRating,
    Branch,
    BranchLinkRequest,
    BranchType,
    BranchVisibility,
    Genre,
    LinkRequestStatus,
    Novel,
    NovelStatus,
)

# =============================================================================
# Novel Serializers
# =============================================================================


class AuthorSerializer(serializers.Serializer):
    """Minimal author info for embedding."""

    id = serializers.IntegerField(read_only=True)
    nickname = serializers.CharField(read_only=True)


class NovelCreateSerializer(serializers.Serializer):
    """Serializer for creating a new novel."""

    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    cover_image_url = serializers.URLField(required=False, allow_blank=True, default="")
    genre = serializers.ChoiceField(choices=Genre.choices)
    age_rating = serializers.ChoiceField(
        choices=AgeRating.choices, required=False, default=AgeRating.ALL
    )
    status = serializers.ChoiceField(
        choices=NovelStatus.choices, required=False, default=NovelStatus.ONGOING
    )
    allow_branching = serializers.BooleanField(required=False, default=True)


class NovelDetailSerializer(serializers.ModelSerializer):
    """Serializer for novel detail view."""

    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Novel
        fields = [
            "id",
            "title",
            "description",
            "cover_image_url",
            "genre",
            "age_rating",
            "status",
            "allow_branching",
            "total_view_count",
            "total_like_count",
            "total_chapter_count",
            "branch_count",
            "linked_branch_count",
            "author",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class NovelListSerializer(serializers.ModelSerializer):
    """Serializer for novel list view (summary)."""

    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Novel
        fields = [
            "id",
            "title",
            "cover_image_url",
            "genre",
            "age_rating",
            "status",
            "total_view_count",
            "total_like_count",
            "branch_count",
            "author",
            "created_at",
        ]
        read_only_fields = fields


class NovelUpdateSerializer(serializers.Serializer):
    """Serializer for updating a novel."""

    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    cover_image_url = serializers.URLField(required=False, allow_blank=True)
    genre = serializers.ChoiceField(choices=Genre.choices, required=False)
    age_rating = serializers.ChoiceField(choices=AgeRating.choices, required=False)
    status = serializers.ChoiceField(choices=NovelStatus.choices, required=False)
    allow_branching = serializers.BooleanField(required=False)


# =============================================================================
# Branch Serializers
# =============================================================================


class BranchCreateSerializer(serializers.Serializer):
    """Serializer for creating/forking a branch."""

    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    cover_image_url = serializers.URLField(required=False, allow_blank=True, default="")
    branch_type = serializers.ChoiceField(
        choices=BranchType.choices, required=False, default=BranchType.FAN_FIC
    )
    fork_point_chapter = serializers.IntegerField(required=False, allow_null=True)


class BranchDetailSerializer(serializers.ModelSerializer):
    """Serializer for branch detail view."""

    author = AuthorSerializer(read_only=True)
    novel_id = serializers.IntegerField(source="novel.id", read_only=True)
    parent_branch_id = serializers.IntegerField(
        source="parent_branch.id", read_only=True, allow_null=True
    )

    class Meta:
        model = Branch
        fields = [
            "id",
            "novel_id",
            "name",
            "description",
            "cover_image_url",
            "is_main",
            "branch_type",
            "visibility",
            "canon_status",
            "parent_branch_id",
            "fork_point_chapter",
            "vote_count",
            "vote_threshold",
            "view_count",
            "chapter_count",
            "author",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class BranchListSerializer(serializers.ModelSerializer):
    """Serializer for branch list view (summary)."""

    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Branch
        fields = [
            "id",
            "name",
            "cover_image_url",
            "is_main",
            "branch_type",
            "visibility",
            "vote_count",
            "view_count",
            "chapter_count",
            "author",
            "created_at",
        ]
        read_only_fields = fields


class BranchVisibilityUpdateSerializer(serializers.Serializer):
    """Serializer for updating branch visibility."""

    visibility = serializers.ChoiceField(choices=BranchVisibility.choices)


# =============================================================================
# BranchLinkRequest Serializers
# =============================================================================


class BranchLinkRequestCreateSerializer(serializers.Serializer):
    """Serializer for creating a link request."""

    request_message = serializers.CharField(required=False, allow_blank=True, default="")


class BranchLinkRequestReviewSerializer(serializers.Serializer):
    """Serializer for reviewing (approve/reject) a link request."""

    status = serializers.ChoiceField(
        choices=[LinkRequestStatus.APPROVED, LinkRequestStatus.REJECTED]
    )
    review_comment = serializers.CharField(required=False, allow_blank=True, default="")


class BranchLinkRequestSerializer(serializers.ModelSerializer):
    """Serializer for link request detail."""

    branch_id = serializers.IntegerField(source="branch.id", read_only=True)
    reviewer_id = serializers.IntegerField(source="reviewer.id", read_only=True, allow_null=True)

    class Meta:
        model = BranchLinkRequest
        fields = [
            "id",
            "branch_id",
            "status",
            "request_message",
            "reviewer_id",
            "review_comment",
            "reviewed_at",
            "created_at",
        ]
        read_only_fields = fields
