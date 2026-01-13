"""
TDD: ReadingService, BookmarkService 테스트
RED → GREEN → REFACTOR
"""

import pytest
from model_bakery import baker

from apps.interactions.models import Bookmark, ReadingLog
from apps.interactions.services import BookmarkService, ReadingService

pytestmark = pytest.mark.django_db


class TestReadingServiceRecordReading:
    """ReadingService.record_reading() 테스트"""

    def test_record_reading_creates_log(self) -> None:
        """읽은 기록 생성"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        log = ReadingService.record_reading(
            user=user,
            chapter_id=chapter.id,
            progress=0.5,
        )

        assert log.id is not None
        assert log.user == user
        assert log.chapter == chapter
        assert float(log.progress) == 0.5
        assert log.is_completed is False

    def test_record_reading_updates_existing(self) -> None:
        """기존 기록 업데이트"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        # 첫 번째 기록
        log1 = ReadingService.record_reading(
            user=user,
            chapter_id=chapter.id,
            progress=0.3,
        )

        # 두 번째 기록 (업데이트)
        log2 = ReadingService.record_reading(
            user=user,
            chapter_id=chapter.id,
            progress=0.8,
        )

        assert log1.id == log2.id
        assert float(log2.progress) == 0.8
        assert ReadingLog.objects.filter(user=user, chapter=chapter).count() == 1

    def test_record_reading_marks_completed(self) -> None:
        """진행률 1.0이면 완독 처리"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        log = ReadingService.record_reading(
            user=user,
            chapter_id=chapter.id,
            progress=1.0,
        )

        assert log.is_completed is True


class TestReadingServiceGetRecentReads:
    """ReadingService.get_recent_reads() 테스트"""

    def test_get_recent_reads(self) -> None:
        """최근 읽은 목록 조회"""
        user = baker.make("users.User")
        chapters = baker.make("contents.Chapter", _quantity=5)

        for _i, chapter in enumerate(chapters):
            ReadingService.record_reading(
                user=user,
                chapter_id=chapter.id,
                progress=0.5,
            )

        result = ReadingService.get_recent_reads(user=user, limit=3)

        assert len(result) == 3

    def test_get_recent_reads_excludes_other_users(self) -> None:
        """다른 사용자 기록 제외"""
        user1 = baker.make("users.User")
        user2 = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        ReadingService.record_reading(user=user1, chapter_id=chapter.id, progress=0.5)
        ReadingService.record_reading(user=user2, chapter_id=chapter.id, progress=0.5)

        result = ReadingService.get_recent_reads(user=user1)

        assert len(result) == 1
        assert result[0].user == user1

    def test_get_recent_reads_order_by_read_at(self) -> None:
        """읽은 시간 순 정렬"""
        user = baker.make("users.User")
        chapter1 = baker.make("contents.Chapter")
        chapter2 = baker.make("contents.Chapter")

        ReadingService.record_reading(user=user, chapter_id=chapter1.id, progress=0.5)
        ReadingService.record_reading(user=user, chapter_id=chapter2.id, progress=0.5)

        result = ReadingService.get_recent_reads(user=user)

        # 가장 최근 읽은 것이 먼저
        assert result[0].chapter == chapter2


class TestReadingServiceGetContinueReading:
    """ReadingService.get_continue_reading() 테스트"""

    def test_get_continue_reading_per_branch(self) -> None:
        """브랜치별 이어보기 정보"""
        user = baker.make("users.User")
        branch = baker.make("novels.Branch")
        chapter1 = baker.make("contents.Chapter", branch=branch, chapter_number=1)
        chapter2 = baker.make("contents.Chapter", branch=branch, chapter_number=2)
        baker.make("contents.Chapter", branch=branch, chapter_number=3)

        ReadingService.record_reading(user=user, chapter_id=chapter1.id, progress=1.0)
        ReadingService.record_reading(user=user, chapter_id=chapter2.id, progress=0.5)

        result = ReadingService.get_continue_reading(user=user, branch_id=branch.id)

        # 마지막으로 읽던 회차 (미완독 우선)
        assert result["chapter"].id == chapter2.id
        assert float(result["progress"]) == 0.5

    def test_get_continue_reading_next_chapter(self) -> None:
        """완독 후 다음 회차 추천"""
        user = baker.make("users.User")
        branch = baker.make("novels.Branch")
        chapter1 = baker.make("contents.Chapter", branch=branch, chapter_number=1)
        chapter2 = baker.make("contents.Chapter", branch=branch, chapter_number=2)

        ReadingService.record_reading(user=user, chapter_id=chapter1.id, progress=1.0)

        result = ReadingService.get_continue_reading(user=user, branch_id=branch.id)

        # 다음 회차 추천
        assert result["chapter"].id == chapter2.id
        assert result["progress"] == 0

    def test_get_continue_reading_no_history(self) -> None:
        """읽은 기록 없으면 첫 회차"""
        user = baker.make("users.User")
        branch = baker.make("novels.Branch")
        chapter1 = baker.make("contents.Chapter", branch=branch, chapter_number=1)
        baker.make("contents.Chapter", branch=branch, chapter_number=2)

        result = ReadingService.get_continue_reading(user=user, branch_id=branch.id)

        assert result["chapter"].id == chapter1.id
        assert result["progress"] == 0


class TestBookmarkServiceAdd:
    """BookmarkService.add_bookmark() 테스트"""

    def test_add_bookmark(self) -> None:
        """북마크 추가"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        bookmark = BookmarkService.add_bookmark(
            user=user,
            chapter_id=chapter.id,
            scroll_position=0.3,
            note="여기서 중요한 내용",
        )

        assert bookmark.id is not None
        assert bookmark.user == user
        assert bookmark.chapter == chapter
        assert float(bookmark.scroll_position) == 0.3
        assert bookmark.note == "여기서 중요한 내용"

    def test_add_bookmark_duplicate_updates(self) -> None:
        """중복 북마크는 업데이트"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        bm1 = BookmarkService.add_bookmark(
            user=user,
            chapter_id=chapter.id,
            scroll_position=0.3,
            note="첫 번째",
        )
        bm2 = BookmarkService.add_bookmark(
            user=user,
            chapter_id=chapter.id,
            scroll_position=0.7,
            note="두 번째",
        )

        assert bm1.id == bm2.id
        assert bm2.note == "두 번째"
        assert Bookmark.objects.filter(user=user, chapter=chapter).count() == 1


class TestBookmarkServiceRemove:
    """BookmarkService.remove_bookmark() 테스트"""

    def test_remove_bookmark(self) -> None:
        """북마크 삭제"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")
        bookmark = baker.make("interactions.Bookmark", user=user, chapter=chapter)

        BookmarkService.remove_bookmark(user=user, chapter_id=chapter.id)

        assert not Bookmark.objects.filter(id=bookmark.id).exists()

    def test_remove_nonexistent_bookmark_no_error(self) -> None:
        """존재하지 않는 북마크 삭제 시 에러 없음"""
        user = baker.make("users.User")

        # 에러 없이 실행
        BookmarkService.remove_bookmark(user=user, chapter_id=99999)


class TestBookmarkServiceGetBookmarks:
    """BookmarkService.get_bookmarks() 테스트"""

    def test_get_bookmarks(self) -> None:
        """북마크 목록 조회"""
        user = baker.make("users.User")
        chapters = baker.make("contents.Chapter", _quantity=3)

        for chapter in chapters:
            BookmarkService.add_bookmark(user=user, chapter_id=chapter.id)

        result = BookmarkService.get_bookmarks(user=user)

        assert len(result) == 3

    def test_get_bookmarks_excludes_other_users(self) -> None:
        """다른 사용자 북마크 제외"""
        user1 = baker.make("users.User")
        user2 = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        BookmarkService.add_bookmark(user=user1, chapter_id=chapter.id)
        BookmarkService.add_bookmark(user=user2, chapter_id=chapter.id)

        result = BookmarkService.get_bookmarks(user=user1)

        assert len(result) == 1
        assert result[0].user == user1
