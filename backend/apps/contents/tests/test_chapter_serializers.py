"""
ChapterSerializer Tests - TDD approach for Chapter serializers.

Tests:
- ChapterCreateSerializer: Validate chapter creation input
- ChapterDetailSerializer: Full chapter detail output
- ChapterListSerializer: Summary for list view
- ChapterUpdateSerializer: Partial update validation
"""

from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker

from apps.contents.models import AccessType, Chapter, ChapterStatus
from apps.contents.serializers import (
    ChapterCreateSerializer,
    ChapterDetailSerializer,
    ChapterListSerializer,
    ChapterScheduleSerializer,
    ChapterUpdateSerializer,
)
from apps.novels.models import Branch


@pytest.mark.django_db
class TestChapterCreateSerializer:
    """Tests for ChapterCreateSerializer."""

    def test_valid_data(self):
        """Should validate correct input data."""
        data = {
            "title": "Chapter 1",
            "content": "# Hello World\n\nThis is content.",
        }

        serializer = ChapterCreateSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["title"] == "Chapter 1"
        assert serializer.validated_data["content"] == "# Hello World\n\nThis is content."

    def test_default_access_type(self):
        """Should default to FREE access type."""
        data = {"title": "Test", "content": "Content"}

        serializer = ChapterCreateSerializer(data=data)
        serializer.is_valid()

        assert serializer.validated_data.get("access_type", AccessType.FREE) == AccessType.FREE

    def test_with_subscription_access_type(self):
        """Should accept SUBSCRIPTION access type with price."""
        data = {
            "title": "Premium Chapter",
            "content": "Premium content",
            "access_type": AccessType.SUBSCRIPTION,
            "price": 100,
        }

        serializer = ChapterCreateSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["access_type"] == AccessType.SUBSCRIPTION
        assert serializer.validated_data["price"] == 100

    def test_missing_title_is_invalid(self):
        """Should reject data without title."""
        data = {"content": "Content only"}

        serializer = ChapterCreateSerializer(data=data)

        assert not serializer.is_valid()
        assert "title" in serializer.errors

    def test_missing_content_is_invalid(self):
        """Should reject data without content."""
        data = {"title": "Title only"}

        serializer = ChapterCreateSerializer(data=data)

        assert not serializer.is_valid()
        assert "content" in serializer.errors


@pytest.mark.django_db
class TestChapterDetailSerializer:
    """Tests for ChapterDetailSerializer."""

    def test_serializes_all_fields(self):
        """Should serialize all chapter detail fields."""
        branch = baker.make(Branch)
        chapter = baker.make(
            Chapter,
            branch=branch,
            chapter_number=1,
            title="Test Chapter",
            content="# Hello",
            content_html="<h1>Hello</h1>",
            word_count=1,
            status=ChapterStatus.PUBLISHED,
            access_type=AccessType.FREE,
            view_count=100,
            like_count=10,
            comment_count=5,
        )

        serializer = ChapterDetailSerializer(chapter)
        data = serializer.data

        assert data["id"] == chapter.id
        assert data["chapter_number"] == 1
        assert data["title"] == "Test Chapter"
        assert data["content_html"] == "<h1>Hello</h1>"
        assert data["word_count"] == 1
        assert data["status"] == ChapterStatus.PUBLISHED
        assert data["access_type"] == AccessType.FREE
        assert data["view_count"] == 100
        assert data["like_count"] == 10
        assert data["comment_count"] == 5

    def test_includes_navigation_info(self):
        """Should include prev/next chapter navigation."""
        branch = baker.make(Branch)
        baker.make(
            Chapter,
            branch=branch,
            chapter_number=1,
            title="Chapter 1",
            status=ChapterStatus.PUBLISHED,
        )
        ch2 = baker.make(
            Chapter,
            branch=branch,
            chapter_number=2,
            title="Chapter 2",
            status=ChapterStatus.PUBLISHED,
        )
        baker.make(
            Chapter,
            branch=branch,
            chapter_number=3,
            title="Chapter 3",
            status=ChapterStatus.PUBLISHED,
        )

        # Test middle chapter
        serializer = ChapterDetailSerializer(ch2, context={"branch_id": branch.id})
        data = serializer.data

        assert data["prev_chapter"]["chapter_number"] == 1
        assert data["next_chapter"]["chapter_number"] == 3


@pytest.mark.django_db
class TestChapterListSerializer:
    """Tests for ChapterListSerializer."""

    def test_serializes_summary_fields(self):
        """Should serialize only summary fields for list view."""
        branch = baker.make(Branch)
        chapter = baker.make(
            Chapter,
            branch=branch,
            chapter_number=1,
            title="Test Chapter",
            status=ChapterStatus.PUBLISHED,
            access_type=AccessType.FREE,
            view_count=100,
            like_count=10,
        )

        serializer = ChapterListSerializer(chapter)
        data = serializer.data

        assert data["id"] == chapter.id
        assert data["chapter_number"] == 1
        assert data["title"] == "Test Chapter"
        assert data["status"] == ChapterStatus.PUBLISHED
        assert data["access_type"] == AccessType.FREE
        assert data["view_count"] == 100
        assert data["like_count"] == 10
        # Should NOT include content_html
        assert "content_html" not in data


@pytest.mark.django_db
class TestChapterUpdateSerializer:
    """Tests for ChapterUpdateSerializer."""

    def test_partial_update_title_only(self):
        """Should allow updating only title."""
        data = {"title": "New Title"}

        serializer = ChapterUpdateSerializer(data=data, partial=True)

        assert serializer.is_valid()
        assert serializer.validated_data["title"] == "New Title"

    def test_partial_update_content_only(self):
        """Should allow updating only content."""
        data = {"content": "New content"}

        serializer = ChapterUpdateSerializer(data=data, partial=True)

        assert serializer.is_valid()
        assert serializer.validated_data["content"] == "New content"


@pytest.mark.django_db
class TestChapterScheduleSerializer:
    """Tests for ChapterScheduleSerializer."""

    def test_valid_future_time(self):
        """Should accept future scheduled_at time."""
        future_time = timezone.now() + timedelta(days=1)
        data = {"scheduled_at": future_time.isoformat()}

        serializer = ChapterScheduleSerializer(data=data)

        assert serializer.is_valid()

    def test_missing_scheduled_at_is_invalid(self):
        """Should reject data without scheduled_at."""
        serializer = ChapterScheduleSerializer(data={})

        assert not serializer.is_valid()
        assert "scheduled_at" in serializer.errors
