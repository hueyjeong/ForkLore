"""
ChapterService - Business logic for Chapter management.
WikiService - Business logic for Wiki management.
"""

import builtins
import re
from datetime import datetime

import markdown
from django.core.exceptions import PermissionDenied
from django.db.models import F, Prefetch, Q, QuerySet
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
        브랜치에 새 장(chapter)을 생성하여 초안(DRAFT) 상태로 저장합니다.
        
        Parameters:
            branch (Branch): 장을 생성할 브랜치 인스턴스
            title (str): 장 제목
            content (str): 마크다운 형식의 원문 콘텐츠
            access_type (str): 접근 유형 (`AccessType.FREE` 또는 구독형)
            price (int): 구독형일 때 적용되는 가격(정수)
        
        Returns:
            Chapter: 생성된 Chapter 인스턴스
        """
        # Get next chapter number
        last_chapter = Chapter.objects.filter(branch=branch).order_by("-chapter_number").first()
        next_number = (last_chapter.chapter_number + 1) if last_chapter else 1

        # Convert markdown to HTML
        content_html = self.convert_markdown(content)

        # Calculate word count
        word_count = self.calculate_word_count(content)

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
        초안 상태의 회차 정보를 갱신한다.
        
        content가 제공되면 마크다운을 HTML로 변환하고 content_html 및 word_count를 갱신한다.
        
        Parameters:
            chapter (Chapter): 갱신할 Chapter 객체
            title (str | None): 새 제목 (선택)
            content (str | None): 새 마크다운 내용 (선택)
            access_type (str | None): 접근 유형 (선택)
            price (int | None): 가격 (선택)
        
        Returns:
            Chapter: 갱신된 Chapter 인스턴스
        
        Raises:
            ValueError: 회차가 이미 발행되어 있고 content를 수정하려 할 경우 발생한다.
        """
        if chapter.status == ChapterStatus.PUBLISHED and content is not None:
            raise ValueError("발행된 회차의 내용은 수정할 수 없습니다.")

        if title is not None:
            chapter.title = title

        if content is not None:
            chapter.content = content
            chapter.content_html = self.convert_markdown(content)
            chapter.word_count = self.calculate_word_count(content)

        if access_type is not None:
            chapter.access_type = access_type

        if price is not None:
            chapter.price = price

        chapter.save()
        return chapter

    def publish(self, chapter: Chapter) -> Chapter:
        """
        초안 또는 예약된 회차를 발행 상태로 전환합니다.
        
        매개변수:
            chapter (Chapter): 발행할 Chapter 인스턴스
        
        반환:
            Chapter: 발행된 Chapter 인스턴스
        
        예외:
            ValueError: chapter가 이미 발행된 상태일 경우
        """
        if chapter.status == ChapterStatus.PUBLISHED:
            raise ValueError("이미 발행된 회차입니다.")

        chapter.status = ChapterStatus.PUBLISHED
        chapter.published_at = timezone.now()
        chapter.save()

        # Update branch chapter_count and version
        branch = chapter.branch
        branch.chapter_count = F("chapter_count") + 1
        branch.version = F("version") + 1
        branch.save(update_fields=["chapter_count", "version"])

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
        브랜치에 속한 챕터 목록을 조회한다.
        
        Parameters:
            branch_id (int): 조회할 브랜치의 ID.
            published_only (bool): True이면 공개 상태(PUBLISHED)인 챕터만 포함한다.
        
        Returns:
            QuerySet[Chapter]: chapter_number 순으로 정렬된 챕터 쿼리셋.
        """
        qs = Chapter.objects.filter(branch_id=branch_id).order_by("chapter_number")

        if published_only:
            qs = qs.filter(status=ChapterStatus.PUBLISHED)

        return qs

    def convert_markdown(self, content: str) -> str:
        """
        마크다운 형식의 텍스트를 HTML로 변환합니다.
        
        Returns:
            html (str): 변환된 HTML 문자열
        """
        md = markdown.Markdown(extensions=["extra", "codehilite", "toc"])
        return md.convert(content)

    def calculate_word_count(self, content: str) -> int:
        """
        문서 콘텐츠의 단어 수를 계산한다. 한국어는 문자 단위로, 영어는 공백으로 구분된 단어 단위로 계산한다.
        
        본문의 기본 마크다운 문법 기호(예: # * _ ` [ ] ( ) >)와 연속 공백을 제거한 뒤 공백으로 분리하여 개수를 반환한다.
        
        Returns:
            int: 계산된 단어(또는 문자) 수. 내용이 비어있으면 0을 반환한다.
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
        ID에 해당하는 위키 항목을 관련 태그와 정렬된 스냅샷과 함께 조회합니다.
        
        Parameters:
            wiki_id (int): 조회할 위키의 ID
        
        Returns:
            WikiEntry: 태그가 프리페치되고 스냅샷이 valid_from_chapter 기준으로 오름차순 정렬된 WikiEntry 객체
        
        Raises:
            ValueError: 지정한 ID의 위키가 존재하지 않을 경우
        """
        try:
            return WikiEntry.objects.prefetch_related(
                "tags", Prefetch("snapshots", WikiSnapshot.objects.order_by("valid_from_chapter"))
            ).get(id=wiki_id)
        except WikiEntry.DoesNotExist as e:
            raise ValueError("존재하지 않는 위키입니다.") from e

    @staticmethod
    def retrieve_for_snapshots(wiki_id: int) -> WikiEntry:
        """
        위키 항목의 스냅샷을 가볍게(prefetch) 로드하여 해당 위키 항목을 반환한다.
        
        Parameters:
            wiki_id (int): 조회할 위키 항목의 ID.
        
        Returns:
            WikiEntry: 스냅샷이 `valid_from_chapter` 오름차순으로 prefetched된 위키 항목.
        
        Raises:
            ValueError: 지정한 ID의 위키가 존재하지 않을 경우.
        """
        try:
            return WikiEntry.objects.prefetch_related(
                Prefetch("snapshots", WikiSnapshot.objects.order_by("valid_from_chapter"))
            ).get(id=wiki_id)
        except WikiEntry.DoesNotExist as e:
            raise ValueError("존재하지 않는 위키입니다.") from e

    @staticmethod
    def list(
        branch_id: int,
        tag_id: int | None = None,
        current_chapter: int | None = None,
    ) -> QuerySet[WikiEntry]:
        """
        브랜치에 속한 위키 항목을 이름 순으로 조회한다.
        
        Parameters:
            branch_id (int): 조회할 브랜치의 ID.
            tag_id (int | None): 주어진 경우 해당 태그를 가진 항목만 필터한다.
            current_chapter (int | None): 주어진 경우 first_appearance가 이 값보다 작거나 같거나 비어있는 항목만 포함하여 현재 챕터 기준으로 노출 가능한 항목을 필터한다.
        
        Returns:
            QuerySet[WikiEntry]: 조건에 맞는 WikiEntry 객체들의 QuerySet(이름 순 정렬).
        """
        qs = WikiEntry.objects.filter(branch_id=branch_id).prefetch_related("tags")

        if tag_id is not None:
            qs = qs.filter(tags__id=tag_id)

        if current_chapter is not None:
            qs = qs.filter(
                Q(first_appearance__lte=current_chapter) | Q(first_appearance__isnull=True)
            )

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