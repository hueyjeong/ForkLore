"""
ChapterService - Business logic for Chapter management.
"""

from datetime import datetime
from typing import Optional
import markdown
import re

from django.db.models import QuerySet
from django.utils import timezone

from apps.contents.models import Chapter, ChapterStatus, AccessType


class ChapterService:
    """Service for managing chapters."""

    def create(
        self,
        branch,
        title: str,
        content: str,
        access_type: str = AccessType.FREE,
        price: int = 0,
    ) -> Chapter:
        """
        Create a new chapter in DRAFT status.

        Args:
            branch: Branch instance
            title: Chapter title
            content: Markdown content
            access_type: FREE or SUBSCRIPTION
            price: Price for subscription chapters

        Returns:
            Created Chapter instance
        """
        # Get next chapter number
        last_chapter = Chapter.objects.filter(branch=branch).order_by("-chapter_number").first()
        next_number = (last_chapter.chapter_number + 1) if last_chapter else 1

        # Convert markdown to HTML
        content_html = self._convert_markdown(content)

        # Calculate word count
        word_count = self._calculate_word_count(content)

        chapter = Chapter.objects.create(
            branch=branch,
            chapter_number=next_number,
            title=title,
            content=content,
            content_html=content_html,
            word_count=word_count,
            status=ChapterStatus.DRAFT,
            access_type=access_type,
            price=price,
        )

        return chapter

    def update(
        self,
        chapter: Chapter,
        title: Optional[str] = None,
        content: Optional[str] = None,
        access_type: Optional[str] = None,
        price: Optional[int] = None,
    ) -> Chapter:
        """
        Update a draft chapter.

        Args:
            chapter: Chapter to update
            title: New title (optional)
            content: New markdown content (optional)
            access_type: New access type (optional)
            price: New price (optional)

        Returns:
            Updated Chapter instance

        Raises:
            ValueError: If chapter is already published
        """
        if chapter.status == ChapterStatus.PUBLISHED and content is not None:
            raise ValueError("발행된 회차의 내용은 수정할 수 없습니다.")

        if title is not None:
            chapter.title = title

        if content is not None:
            chapter.content = content
            chapter.content_html = self._convert_markdown(content)
            chapter.word_count = self._calculate_word_count(content)

        if access_type is not None:
            chapter.access_type = access_type

        if price is not None:
            chapter.price = price

        chapter.save()
        return chapter

    def publish(self, chapter: Chapter) -> Chapter:
        """
        Publish a draft or scheduled chapter.

        Args:
            chapter: Chapter to publish

        Returns:
            Published Chapter instance

        Raises:
            ValueError: If chapter is already published
        """
        if chapter.status == ChapterStatus.PUBLISHED:
            raise ValueError("이미 발행된 회차입니다.")

        chapter.status = ChapterStatus.PUBLISHED
        chapter.published_at = timezone.now()
        chapter.save()

        # Update branch chapter_count
        branch = chapter.branch
        branch.chapter_count += 1
        branch.save(update_fields=["chapter_count"])

        return chapter

    def schedule(self, chapter: Chapter, scheduled_at: datetime) -> Chapter:
        """
        Schedule a chapter for future publication.

        Args:
            chapter: Chapter to schedule
            scheduled_at: When to publish

        Returns:
            Scheduled Chapter instance

        Raises:
            ValueError: If scheduled_at is in the past or chapter is published
        """
        if chapter.status == ChapterStatus.PUBLISHED:
            raise ValueError("발행된 회차는 예약할 수 없습니다.")

        if scheduled_at <= timezone.now():
            raise ValueError("과거 시간으로 예약할 수 없습니다.")

        chapter.status = ChapterStatus.SCHEDULED
        chapter.scheduled_at = scheduled_at
        chapter.save()

        return chapter

    def retrieve(self, branch_id: int, chapter_number: int) -> Optional[Chapter]:
        """
        Retrieve a chapter by branch and chapter number.

        Args:
            branch_id: Branch ID
            chapter_number: Chapter number within branch

        Returns:
            Chapter instance or None if not found
        """
        try:
            return Chapter.objects.get(branch_id=branch_id, chapter_number=chapter_number)
        except Chapter.DoesNotExist:
            return None

    def list(self, branch_id: int, published_only: bool = False) -> QuerySet[Chapter]:
        """
        List chapters for a branch.

        Args:
            branch_id: Branch ID
            published_only: If True, only return published chapters

        Returns:
            QuerySet of chapters ordered by chapter_number
        """
        qs = Chapter.objects.filter(branch_id=branch_id).order_by("chapter_number")

        if published_only:
            qs = qs.filter(status=ChapterStatus.PUBLISHED)

        return qs

    def _convert_markdown(self, content: str) -> str:
        """Convert markdown content to HTML."""
        md = markdown.Markdown(extensions=["extra", "codehilite", "toc"])
        return md.convert(content)

    def _calculate_word_count(self, content: str) -> int:
        """
        Calculate word count from content.
        For Korean, counts characters. For English, counts words.
        """
        # Remove markdown syntax
        plain_text = re.sub(r"[#*_`\[\]()>]", "", content)
        plain_text = re.sub(r"\s+", " ", plain_text).strip()

        if not plain_text:
            return 0

        # Count words (split by whitespace)
        # This works reasonably for mixed Korean/English content
        words = plain_text.split()
        return len(words)
