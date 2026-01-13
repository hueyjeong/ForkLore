"""
Serializers for Novel API.

Includes:
- NovelCreateSerializer: For creating novels
- NovelDetailSerializer: For detailed view with nested author
- NovelListSerializer: For list view with summary
- NovelUpdateSerializer: For partial updates
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Novel, Branch, Genre, AgeRating, NovelStatus

User = get_user_model()


class AuthorSummarySerializer(serializers.ModelSerializer):
    """Author summary for nested representation."""

    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image_url"]
        read_only_fields = fields


class NovelCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new novel."""

    class Meta:
        model = Novel
        fields = [
            "title",
            "description",
            "cover_image_url",
            "genre",
            "age_rating",
            "allow_branching",
        ]
        extra_kwargs = {
            "title": {"required": True},
            "genre": {"required": True},
            "description": {"required": False, "allow_blank": True},
            "cover_image_url": {"required": False, "allow_blank": True},
            "age_rating": {"required": False, "default": AgeRating.ALL},
            "allow_branching": {"required": False, "default": True},
        }


class NovelDetailSerializer(serializers.ModelSerializer):
    """Serializer for novel detail view."""

    author = AuthorSummarySerializer(read_only=True)

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

    author = AuthorSummarySerializer(read_only=True)

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


class NovelUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a novel."""

    class Meta:
        model = Novel
        fields = [
            "title",
            "description",
            "cover_image_url",
            "genre",
            "age_rating",
            "status",
            "allow_branching",
        ]
        extra_kwargs = {
            "title": {"required": False},
            "description": {"required": False},
            "cover_image_url": {"required": False},
            "genre": {"required": False},
            "age_rating": {"required": False},
            "status": {"required": False},
            "allow_branching": {"required": False},
        }
