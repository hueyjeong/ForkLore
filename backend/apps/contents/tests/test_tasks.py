"""
Celery tasks Tests - TDD approach for scheduled publishing.

Tests:
- publish_scheduled_chapters: Auto-publish scheduled chapters
"""

from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker

from apps.contents.models import Chapter, ChapterStatus
from apps.contents.tasks import publish_scheduled_chapters
from apps.novels.models import Branch


@pytest.mark.django_db
class TestPublishScheduledChapters:
    """Tests for publish_scheduled_chapters task."""

    def test_publishes_scheduled_chapters_past_time(self):
        """Should publish chapters whose scheduled_at has passed."""
        branch = baker.make(Branch, chapter_count=0)
        past_time = timezone.now() - timedelta(hours=1)

        chapter = baker.make(
            Chapter,
            branch=branch,
            status=ChapterStatus.SCHEDULED,
            scheduled_at=past_time,
        )

        result = publish_scheduled_chapters()

        chapter.refresh_from_db()
        assert chapter.status == ChapterStatus.PUBLISHED
        assert chapter.published_at is not None
        assert result == 1

    def test_does_not_publish_future_chapters(self):
        """Should not publish chapters scheduled for the future."""
        future_time = timezone.now() + timedelta(hours=1)

        chapter = baker.make(
            Chapter,
            status=ChapterStatus.SCHEDULED,
            scheduled_at=future_time,
        )

        result = publish_scheduled_chapters()

        chapter.refresh_from_db()
        assert chapter.status == ChapterStatus.SCHEDULED
        assert chapter.published_at is None
        assert result == 0

    def test_does_not_affect_draft_chapters(self):
        """Should not publish DRAFT chapters."""
        past_time = timezone.now() - timedelta(hours=1)

        chapter = baker.make(
            Chapter,
            status=ChapterStatus.DRAFT,
            scheduled_at=past_time,
        )

        result = publish_scheduled_chapters()

        chapter.refresh_from_db()
        assert chapter.status == ChapterStatus.DRAFT
        assert result == 0

    def test_increments_branch_chapter_count(self):
        """Should increment branch chapter_count when publishing."""
        branch = baker.make(Branch, chapter_count=5)
        past_time = timezone.now() - timedelta(hours=1)

        baker.make(
            Chapter,
            branch=branch,
            status=ChapterStatus.SCHEDULED,
            scheduled_at=past_time,
        )

        publish_scheduled_chapters()

        branch.refresh_from_db()
        assert branch.chapter_count == 6

    def test_publishes_multiple_chapters(self):
        """Should publish all ready chapters in one run."""
        branch = baker.make(Branch, chapter_count=0)
        past_time = timezone.now() - timedelta(hours=1)

        baker.make(
            Chapter,
            branch=branch,
            chapter_number=1,
            status=ChapterStatus.SCHEDULED,
            scheduled_at=past_time,
        )
        baker.make(
            Chapter,
            branch=branch,
            chapter_number=2,
            status=ChapterStatus.SCHEDULED,
            scheduled_at=past_time,
        )
        baker.make(
            Chapter,
            branch=branch,
            chapter_number=3,
            status=ChapterStatus.SCHEDULED,
            scheduled_at=past_time,
        )

        result = publish_scheduled_chapters()

        assert result == 3
        branch.refresh_from_db()
        assert branch.chapter_count == 3
