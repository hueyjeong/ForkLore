"""
ChapterService Tests - TDD approach for Chapter system.

Tests:
- create(): Create a new chapter (draft)
- update(): Update chapter content
- publish(): Publish a draft chapter
- schedule(): Schedule a chapter for future publication
- retrieve(): Get chapter by branch and number
- list(): List chapters for a branch
"""

from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker

from apps.contents.models import AccessType, Chapter, ChapterStatus
from apps.contents.services import ChapterService
from apps.novels.models import Branch


@pytest.mark.django_db
class TestChapterServiceCreate:
    """Tests for ChapterService.create()"""

    def test_create_chapter_as_draft(self):
        """Should create a chapter with DRAFT status by default."""
        service = ChapterService()
        branch = baker.make(Branch)

        chapter = service.create(
            branch=branch,
            title="Chapter 1",
            content="# Hello World\n\nThis is content.",
        )

        assert chapter.id is not None
        assert chapter.branch == branch
        assert chapter.title == "Chapter 1"
        assert chapter.content == "# Hello World\n\nThis is content."
        assert chapter.status == ChapterStatus.DRAFT
        assert chapter.chapter_number == 1
        assert chapter.published_at is None

    def test_create_chapter_auto_increments_number(self):
        """Should auto-increment chapter_number within branch."""
        service = ChapterService()
        branch = baker.make(Branch)
        baker.make(Chapter, branch=branch, chapter_number=1)
        baker.make(Chapter, branch=branch, chapter_number=2)

        chapter = service.create(branch=branch, title="Chapter 3", content="Content")

        assert chapter.chapter_number == 3

    def test_create_chapter_converts_markdown_to_html(self):
        """Should convert markdown content to HTML."""
        service = ChapterService()
        branch = baker.make(Branch)

        chapter = service.create(
            branch=branch,
            title="Test",
            content="# Heading\n\n**Bold text**",
        )

        assert "Heading</h1>" in chapter.content_html
        assert "<strong>Bold text</strong>" in chapter.content_html

    def test_create_chapter_calculates_word_count(self):
        """Should calculate word count from content."""
        service = ChapterService()
        branch = baker.make(Branch)

        chapter = service.create(
            branch=branch,
            title="Test",
            content="This is a test content with several words in it.",
        )

        # Korean word count is character-based for Korean, word-based for English
        assert chapter.word_count > 0

    def test_create_chapter_with_access_type(self):
        """Should set access_type and price when provided."""
        service = ChapterService()
        branch = baker.make(Branch)

        chapter = service.create(
            branch=branch,
            title="Premium Chapter",
            content="Content",
            access_type=AccessType.SUBSCRIPTION,
            price=100,
        )

        assert chapter.access_type == AccessType.SUBSCRIPTION
        assert chapter.price == 100


@pytest.mark.django_db
class TestChapterServiceUpdate:
    """Tests for ChapterService.update()"""

    def test_update_chapter_content(self):
        """Should update chapter content and regenerate HTML."""
        service = ChapterService()
        chapter = baker.make(
            Chapter,
            title="Old Title",
            content="Old content",
            content_html="<p>Old content</p>",
        )

        updated = service.update(
            chapter=chapter,
            title="New Title",
            content="# New Content",
        )

        assert updated.title == "New Title"
        assert updated.content == "# New Content"
        assert "New Content</h1>" in updated.content_html

    def test_update_chapter_recalculates_word_count(self):
        """Should recalculate word_count on content update."""
        service = ChapterService()
        chapter = baker.make(Chapter, content="Short", word_count=1)

        updated = service.update(
            chapter=chapter,
            content="This is a much longer content with many more words now.",
        )

        assert updated.word_count > 1

    def test_update_draft_chapter_only(self):
        """Should raise error when trying to update published chapter content."""
        service = ChapterService()
        chapter = baker.make(
            Chapter,
            status=ChapterStatus.PUBLISHED,
            published_at=timezone.now(),
        )

        with pytest.raises(ValueError, match="발행된 회차"):
            service.update(chapter=chapter, content="New content")


@pytest.mark.django_db
class TestChapterServicePublish:
    """Tests for ChapterService.publish()"""

    def test_publish_draft_chapter(self):
        """Should change status to PUBLISHED and set published_at."""
        service = ChapterService()
        chapter = baker.make(Chapter, status=ChapterStatus.DRAFT)

        published = service.publish(chapter=chapter)

        assert published.status == ChapterStatus.PUBLISHED
        assert published.published_at is not None

    def test_publish_scheduled_chapter(self):
        """Should publish a scheduled chapter."""
        service = ChapterService()
        chapter = baker.make(
            Chapter,
            status=ChapterStatus.SCHEDULED,
            scheduled_at=timezone.now() - timedelta(hours=1),
        )

        published = service.publish(chapter=chapter)

        assert published.status == ChapterStatus.PUBLISHED

    def test_publish_already_published_raises_error(self):
        """Should raise error when chapter is already published."""
        service = ChapterService()
        chapter = baker.make(
            Chapter,
            status=ChapterStatus.PUBLISHED,
            published_at=timezone.now(),
        )

        with pytest.raises(ValueError, match="이미 발행"):
            service.publish(chapter=chapter)

    def test_publish_increments_branch_chapter_count(self):
        """Should increment branch.chapter_count when publishing."""
        service = ChapterService()
        branch = baker.make(Branch, chapter_count=5)
        chapter = baker.make(Chapter, branch=branch, status=ChapterStatus.DRAFT)

        service.publish(chapter=chapter)

        branch.refresh_from_db()
        assert branch.chapter_count == 6


@pytest.mark.django_db
class TestChapterServiceSchedule:
    """Tests for ChapterService.schedule()"""

    def test_schedule_chapter(self):
        """Should set status to SCHEDULED and scheduled_at."""
        service = ChapterService()
        chapter = baker.make(Chapter, status=ChapterStatus.DRAFT)
        schedule_time = timezone.now() + timedelta(days=1)

        scheduled = service.schedule(chapter=chapter, scheduled_at=schedule_time)

        assert scheduled.status == ChapterStatus.SCHEDULED
        assert scheduled.scheduled_at == schedule_time

    def test_schedule_past_time_raises_error(self):
        """Should raise error when scheduling in the past."""
        service = ChapterService()
        chapter = baker.make(Chapter, status=ChapterStatus.DRAFT)
        past_time = timezone.now() - timedelta(hours=1)

        with pytest.raises(ValueError, match="과거"):
            service.schedule(chapter=chapter, scheduled_at=past_time)

    def test_schedule_published_chapter_raises_error(self):
        """Should raise error when scheduling already published chapter."""
        service = ChapterService()
        chapter = baker.make(
            Chapter,
            status=ChapterStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        future_time = timezone.now() + timedelta(days=1)

        with pytest.raises(ValueError, match="발행된 회차"):
            service.schedule(chapter=chapter, scheduled_at=future_time)


@pytest.mark.django_db
class TestChapterServiceRetrieve:
    """Tests for ChapterService.retrieve()"""

    def test_retrieve_chapter_by_branch_and_number(self):
        """Should retrieve chapter by branch_id and chapter_number."""
        service = ChapterService()
        branch = baker.make(Branch)
        chapter = baker.make(Chapter, branch=branch, chapter_number=5)

        result = service.retrieve(branch_id=branch.id, chapter_number=5)

        assert result == chapter

    def test_retrieve_nonexistent_chapter_returns_none(self):
        """Should return None when chapter doesn't exist."""
        service = ChapterService()
        branch = baker.make(Branch)

        result = service.retrieve(branch_id=branch.id, chapter_number=999)

        assert result is None


@pytest.mark.django_db
class TestChapterServiceList:
    """Tests for ChapterService.list()"""

    def test_list_chapters_for_branch(self):
        """Should return all chapters for a branch ordered by number."""
        service = ChapterService()
        branch = baker.make(Branch)
        ch3 = baker.make(Chapter, branch=branch, chapter_number=3)
        ch1 = baker.make(Chapter, branch=branch, chapter_number=1)
        ch2 = baker.make(Chapter, branch=branch, chapter_number=2)

        result = list(service.list(branch_id=branch.id))

        assert len(result) == 3
        assert result[0] == ch1
        assert result[1] == ch2
        assert result[2] == ch3

    def test_list_excludes_other_branches(self):
        """Should only return chapters for the specified branch."""
        service = ChapterService()
        branch1 = baker.make(Branch)
        branch2 = baker.make(Branch)
        ch1 = baker.make(Chapter, branch=branch1, chapter_number=1)
        baker.make(Chapter, branch=branch2, chapter_number=1)

        result = list(service.list(branch_id=branch1.id))

        assert len(result) == 1
        assert result[0] == ch1

    def test_list_published_only(self):
        """Should filter to only published chapters when specified."""
        service = ChapterService()
        branch = baker.make(Branch)
        published = baker.make(
            Chapter,
            branch=branch,
            chapter_number=1,
            status=ChapterStatus.PUBLISHED,
        )
        baker.make(
            Chapter,
            branch=branch,
            chapter_number=2,
            status=ChapterStatus.DRAFT,
        )

        result = list(service.list(branch_id=branch.id, published_only=True))

        assert len(result) == 1
        assert result[0] == published
