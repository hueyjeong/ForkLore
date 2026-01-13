"""
ChapterService - Business logic for Chapter management.
WikiService - Business logic for Wiki management.
"""

import builtins
import re
from datetime import datetime

import markdown
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.utils import timezone

from apps.contents.models import (
    AccessType,
    Chapter,
    ChapterStatus,
    ContributorType,
    WikiEntry,
    WikiSnapshot,
    WikiTagDefinition,
)
from apps.novels.models import Branch
from apps.users.models import User


class ChapterService:
    """Service for managing chapters."""

    def create(
        self,
        branch: Branch,
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
        title: str | None = None,
        content: str | None = None,
        access_type: str | None = None,
        price: int | None = None,
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

    def retrieve(self, branch_id: int, chapter_number: int) -> Chapter | None:
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


class WikiService:
    """Service for managing wiki entries and tags."""

    @staticmethod
    def _check_branch_author(branch: Branch, user: User) -> None:
        """Check if user is the branch author."""
        if branch.author_id != user.id:
            raise PermissionDenied("브랜치 작가만 수정할 수 있습니다.")

    @staticmethod
    def create(
        branch_id: int,
        user: User,
        name: str,
        image_url: str = "",
        first_appearance: int | None = None,
        hidden_note: str = "",
        ai_metadata: dict | None = None,
        initial_content: str | None = None,
    ) -> WikiEntry:
        """
        Create a new wiki entry.

        Args:
            branch_id: Branch ID
            user: User creating the wiki
            name: Wiki entry name
            image_url: Image URL (optional)
            first_appearance: Chapter number where this first appears (optional)
            hidden_note: Author's private note (optional)
            ai_metadata: AI metadata JSON (optional)
            initial_content: Initial snapshot content (optional)

        Returns:
            Created WikiEntry instance

        Raises:
            PermissionDenied: If user is not branch author
            ValueError: If wiki with same name already exists
        """
        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist as e:
            raise ValueError("존재하지 않는 브랜치입니다.") from e

        WikiService._check_branch_author(branch, user)

        # Check for duplicate name
        if WikiEntry.objects.filter(branch=branch, name=name).exists():
            raise ValueError(f"이미 존재하는 위키 이름입니다: {name}")

        wiki = WikiEntry.objects.create(
            branch=branch,
            name=name,
            image_url=image_url,
            first_appearance=first_appearance,
            hidden_note=hidden_note,
            ai_metadata=ai_metadata,
        )

        # Create initial snapshot if content provided
        if initial_content:
            WikiSnapshot.objects.create(
                wiki_entry=wiki,
                content=initial_content,
                valid_from_chapter=0,
                contributor_type=ContributorType.USER,
                contributor=user,
            )

        return wiki

    @staticmethod
    def update(
        wiki_id: int,
        user: User,
        name: str | None = None,
        image_url: str | None = None,
        first_appearance: int | None = None,
        hidden_note: str | None = None,
        ai_metadata: dict | None = None,
    ) -> WikiEntry:
        """
        Update a wiki entry.

        Args:
            wiki_id: WikiEntry ID
            user: User performing the update
            name: New name (optional)
            image_url: New image URL (optional)
            first_appearance: New first appearance chapter (optional)
            hidden_note: New hidden note (optional)
            ai_metadata: New AI metadata (optional)

        Returns:
            Updated WikiEntry instance

        Raises:
            PermissionDenied: If user is not branch author
            ValueError: If wiki not found
        """
        try:
            wiki = WikiEntry.objects.select_related("branch").get(id=wiki_id)
        except WikiEntry.DoesNotExist as e:
            raise ValueError("존재하지 않는 위키입니다.") from e

        WikiService._check_branch_author(wiki.branch, user)

        if name is not None:
            wiki.name = name
        if image_url is not None:
            wiki.image_url = image_url
        if first_appearance is not None:
            wiki.first_appearance = first_appearance
        if hidden_note is not None:
            wiki.hidden_note = hidden_note
        if ai_metadata is not None:
            wiki.ai_metadata = ai_metadata

        wiki.save()
        return wiki

    @staticmethod
    def retrieve(wiki_id: int) -> WikiEntry:
        """
        Retrieve a wiki entry by ID.

        Args:
            wiki_id: WikiEntry ID

        Returns:
            WikiEntry instance

        Raises:
            ValueError: If wiki not found
        """
        try:
            return (
                WikiEntry.objects.select_related("branch")
                .prefetch_related("tags", "snapshots")
                .get(id=wiki_id)
            )
        except WikiEntry.DoesNotExist as e:
            raise ValueError("존재하지 않는 위키입니다.") from e

    @staticmethod
    def list(
        branch_id: int,
        tag_id: int | None = None,
    ) -> QuerySet[WikiEntry]:
        """
        List wiki entries for a branch.

        Args:
            branch_id: Branch ID
            tag_id: Filter by tag ID (optional)

        Returns:
            QuerySet of WikiEntry
        """
        qs = WikiEntry.objects.filter(branch_id=branch_id).prefetch_related("tags")

        if tag_id is not None:
            qs = qs.filter(tags__id=tag_id)

        return qs.order_by("name")

    @staticmethod
    def delete(wiki_id: int, user: User) -> None:
        """
        Delete a wiki entry.

        Args:
            wiki_id: WikiEntry ID
            user: User performing the deletion

        Raises:
            PermissionDenied: If user is not branch author
            ValueError: If wiki not found
        """
        try:
            wiki = WikiEntry.objects.select_related("branch").get(id=wiki_id)
        except WikiEntry.DoesNotExist as e:
            raise ValueError("존재하지 않는 위키입니다.") from e

        WikiService._check_branch_author(wiki.branch, user)
        wiki.delete()

    @staticmethod
    def update_tags(wiki_id: int, user: User, tag_ids: builtins.list[int]) -> WikiEntry:
        """
        Update tags for a wiki entry.

        Args:
            wiki_id: WikiEntry ID
            user: User performing the update
            tag_ids: List of tag IDs to set

        Returns:
            Updated WikiEntry instance

        Raises:
            PermissionDenied: If user is not branch author
        """
        try:
            wiki = WikiEntry.objects.select_related("branch").get(id=wiki_id)
        except WikiEntry.DoesNotExist as e:
            raise ValueError("존재하지 않는 위키입니다.") from e

        WikiService._check_branch_author(wiki.branch, user)

        # Set tags (replaces existing)
        tags = WikiTagDefinition.objects.filter(id__in=tag_ids, branch=wiki.branch)
        wiki.tags.set(tags)

        return wiki

    # --- Tag Definition Methods ---

    @staticmethod
    def create_tag(
        branch_id: int,
        user: User,
        name: str,
        color: str = "",
        icon: str = "",
        description: str = "",
        display_order: int = 0,
    ) -> WikiTagDefinition:
        """
        Create a new tag definition.

        Args:
            branch_id: Branch ID
            user: User creating the tag
            name: Tag name
            color: Tag color hex code (optional)
            icon: Tag icon name (optional)
            description: Tag description (optional)
            display_order: Display order (optional)

        Returns:
            Created WikiTagDefinition instance
        """
        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist as e:
            raise ValueError("존재하지 않는 브랜치입니다.") from e

        WikiService._check_branch_author(branch, user)

        return WikiTagDefinition.objects.create(
            branch=branch,
            name=name,
            color=color,
            icon=icon,
            description=description,
            display_order=display_order,
        )

    @staticmethod
    def list_tags(branch_id: int) -> QuerySet[WikiTagDefinition]:
        """
        List tag definitions for a branch.

        Args:
            branch_id: Branch ID

        Returns:
            QuerySet of WikiTagDefinition
        """
        return WikiTagDefinition.objects.filter(branch_id=branch_id).order_by(
            "display_order", "name"
        )

    @staticmethod
    def delete_tag(tag_id: int, user: User) -> None:
        """
        Delete a tag definition.

        Args:
            tag_id: WikiTagDefinition ID
            user: User performing the deletion

        Raises:
            PermissionDenied: If user is not branch author
        """
        try:
            tag = WikiTagDefinition.objects.select_related("branch").get(id=tag_id)
        except WikiTagDefinition.DoesNotExist as e:
            raise ValueError("존재하지 않는 태그입니다.") from e

        WikiService._check_branch_author(tag.branch, user)
        tag.delete()

    # --- Snapshot Methods ---

    @staticmethod
    def add_snapshot(
        wiki_id: int,
        user: User,
        content: str,
        valid_from_chapter: int,
    ) -> WikiSnapshot:
        """
        Add a new snapshot to a wiki entry.

        Args:
            wiki_id: WikiEntry ID
            user: User creating the snapshot
            content: Snapshot content (markdown)
            valid_from_chapter: Chapter number from which this snapshot is valid

        Returns:
            Created WikiSnapshot instance

        Raises:
            PermissionDenied: If user is not branch author
            ValueError: If snapshot for this chapter already exists
        """
        try:
            wiki = WikiEntry.objects.select_related("branch").get(id=wiki_id)
        except WikiEntry.DoesNotExist as e:
            raise ValueError("존재하지 않는 위키입니다.") from e

        WikiService._check_branch_author(wiki.branch, user)

        # Check for existing snapshot at this chapter
        if WikiSnapshot.objects.filter(
            wiki_entry=wiki, valid_from_chapter=valid_from_chapter
        ).exists():
            raise ValueError(f"이미 회차 {valid_from_chapter}에 스냅샷이 존재합니다.")

        return WikiSnapshot.objects.create(
            wiki_entry=wiki,
            content=content,
            valid_from_chapter=valid_from_chapter,
            contributor_type=ContributorType.USER,
            contributor=user,
        )

    @staticmethod
    def get_snapshot_for_chapter(
        wiki_id: int,
        chapter_number: int,
    ) -> WikiSnapshot | None:
        """
        Get the appropriate snapshot for a given chapter (spoiler prevention).

        Returns the snapshot with the highest valid_from_chapter that is <= chapter_number.
        This prevents spoilers by only returning content that was valid up to that chapter.

        Args:
            wiki_id: WikiEntry ID
            chapter_number: Current chapter being read

        Returns:
            WikiSnapshot instance or None if no valid snapshot exists
        """
        return (
            WikiSnapshot.objects.filter(
                wiki_entry_id=wiki_id,
                valid_from_chapter__lte=chapter_number,
            )
            .order_by("-valid_from_chapter")
            .first()
        )

    @staticmethod
    def get_wiki_with_context(
        wiki_id: int,
        chapter_number: int,
    ) -> dict:
        """
        Get wiki entry with context-aware snapshot for a specific chapter.

        Args:
            wiki_id: WikiEntry ID
            chapter_number: Current chapter being read

        Returns:
            Dict with 'wiki' and 'snapshot' keys

        Raises:
            ValueError: If wiki not found
        """
        wiki = WikiService.retrieve(wiki_id)
        snapshot = WikiService.get_snapshot_for_chapter(wiki_id, chapter_number)

        return {
            "wiki": wiki,
            "snapshot": snapshot,
        }

    # --- Fork Methods ---

    @staticmethod
    def fork_wiki_entries(
        source_branch_id: int,
        target_branch_id: int,
        user: User,
    ) -> builtins.list[WikiEntry]:
        """
        Fork all wiki entries from source branch to target branch.

        This copies:
        - All WikiTagDefinitions
        - All WikiEntries (with source_wiki reference)
        - All WikiSnapshots

        Args:
            source_branch_id: Source branch ID
            target_branch_id: Target branch ID
            user: User performing the fork

        Returns:
            List of created WikiEntry instances
        """
        try:
            source_branch = Branch.objects.get(id=source_branch_id)
            target_branch = Branch.objects.get(id=target_branch_id)
        except Branch.DoesNotExist as e:
            raise ValueError("존재하지 않는 브랜치입니다.") from e

        # 1. Copy tag definitions and create mapping
        tag_mapping = {}  # old_tag_id -> new_tag
        source_tags = WikiTagDefinition.objects.filter(branch=source_branch)
        for source_tag in source_tags:
            new_tag = WikiTagDefinition.objects.create(
                branch=target_branch,
                name=source_tag.name,
                color=source_tag.color,
                icon=source_tag.icon,
                description=source_tag.description,
                display_order=source_tag.display_order,
            )
            tag_mapping[source_tag.id] = new_tag

        # 2. Copy wiki entries
        forked_wikis = []
        source_wikis = WikiEntry.objects.filter(branch=source_branch).prefetch_related(
            "tags", "snapshots"
        )

        for source_wiki in source_wikis:
            # Create new wiki with source reference
            new_wiki = WikiEntry.objects.create(
                branch=target_branch,
                source_wiki=source_wiki,
                name=source_wiki.name,
                image_url=source_wiki.image_url,
                first_appearance=source_wiki.first_appearance,
                hidden_note=source_wiki.hidden_note,
                ai_metadata=source_wiki.ai_metadata,
            )

            # Copy tags using mapping
            new_tags = [tag_mapping[t.id] for t in source_wiki.tags.all() if t.id in tag_mapping]
            new_wiki.tags.set(new_tags)

            # Copy snapshots
            for source_snapshot in source_wiki.snapshots.all():
                WikiSnapshot.objects.create(
                    wiki_entry=new_wiki,
                    content=source_snapshot.content,
                    valid_from_chapter=source_snapshot.valid_from_chapter,
                    contributor_type=source_snapshot.contributor_type,
                    contributor=source_snapshot.contributor,
                )

            forked_wikis.append(new_wiki)

        return forked_wikis
