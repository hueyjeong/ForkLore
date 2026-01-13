"""
TDD: ReadingLog/Bookmark ViewSet 테스트
RED → GREEN → REFACTOR
"""

import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from apps.interactions.models import Bookmark, ReadingLog

pytestmark = pytest.mark.django_db


class TestReadingHistoryView:
    """GET /api/v1/users/me/reading-history 테스트"""

    def test_reading_history_requires_auth(self) -> None:
        """인증 없이 접근 불가"""
        client = APIClient()
        url = "/api/v1/users/me/reading-history/"

        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_reading_history_returns_user_logs(self) -> None:
        """읽은 기록 목록 반환"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")
        baker.make("interactions.ReadingLog", user=user, chapter=chapter, progress=0.5)

        client = APIClient()
        client.force_authenticate(user=user)
        url = "/api/v1/users/me/reading-history/"

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert float(response.data["results"][0]["progress"]) == 0.5

    def test_reading_history_excludes_other_users(self) -> None:
        """다른 사용자 기록 제외"""
        user1 = baker.make("users.User")
        user2 = baker.make("users.User")
        chapter = baker.make("contents.Chapter")
        baker.make("interactions.ReadingLog", user=user1, chapter=chapter)
        baker.make("interactions.ReadingLog", user=user2, chapter=chapter)

        client = APIClient()
        client.force_authenticate(user=user1)
        url = "/api/v1/users/me/reading-history/"

        response = client.get(url)

        assert len(response.data["results"]) == 1


class TestContinueReadingView:
    """GET /api/v1/branches/{id}/continue-reading 테스트"""

    def test_continue_reading_requires_auth(self) -> None:
        """인증 없이 접근 불가"""
        client = APIClient()
        branch = baker.make("novels.Branch")
        url = f"/api/v1/novels/branches/{branch.id}/continue-reading/"

        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_continue_reading_returns_chapter(self) -> None:
        """이어보기 정보 반환"""
        user = baker.make("users.User")
        branch = baker.make("novels.Branch")
        chapter1 = baker.make("contents.Chapter", branch=branch, chapter_number=1)
        chapter2 = baker.make("contents.Chapter", branch=branch, chapter_number=2)
        baker.make(
            "interactions.ReadingLog", user=user, chapter=chapter1, progress=1.0, is_completed=True
        )

        client = APIClient()
        client.force_authenticate(user=user)
        url = f"/api/v1/novels/branches/{branch.id}/continue-reading/"

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["chapter"]["id"] == chapter2.id
        assert float(response.data["progress"]) == 0

    def test_continue_reading_no_history(self) -> None:
        """기록 없으면 첫 회차"""
        user = baker.make("users.User")
        branch = baker.make("novels.Branch")
        chapter1 = baker.make("contents.Chapter", branch=branch, chapter_number=1)

        client = APIClient()
        client.force_authenticate(user=user)
        url = f"/api/v1/novels/branches/{branch.id}/continue-reading/"

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["chapter"]["id"] == chapter1.id


class TestBookmarkListView:
    """GET /api/v1/users/me/bookmarks 테스트"""

    def test_bookmarks_requires_auth(self) -> None:
        """인증 없이 접근 불가"""
        client = APIClient()
        url = "/api/v1/users/me/bookmarks/"

        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_bookmarks_returns_user_bookmarks(self) -> None:
        """북마크 목록 반환"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")
        baker.make("interactions.Bookmark", user=user, chapter=chapter, note="테스트")

        client = APIClient()
        client.force_authenticate(user=user)
        url = "/api/v1/users/me/bookmarks/"

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["note"] == "테스트"


class TestChapterBookmarkView:
    """POST/DELETE /api/v1/chapters/{id}/bookmark 테스트"""

    def test_add_bookmark_requires_auth(self) -> None:
        """인증 없이 접근 불가"""
        client = APIClient()
        chapter = baker.make("contents.Chapter")
        url = f"/api/v1/chapters/{chapter.id}/bookmark/"

        response = client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_bookmark(self) -> None:
        """북마크 추가"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        client = APIClient()
        client.force_authenticate(user=user)
        url = f"/api/v1/chapters/{chapter.id}/bookmark/"

        response = client.post(url, {"scroll_position": 0.5, "note": "중요 장면"})

        assert response.status_code == status.HTTP_201_CREATED
        assert Bookmark.objects.filter(user=user, chapter=chapter).exists()

    def test_remove_bookmark(self) -> None:
        """북마크 삭제"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")
        baker.make("interactions.Bookmark", user=user, chapter=chapter)

        client = APIClient()
        client.force_authenticate(user=user)
        url = f"/api/v1/chapters/{chapter.id}/bookmark/"

        response = client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Bookmark.objects.filter(user=user, chapter=chapter).exists()


class TestRecordReadingView:
    """POST /api/v1/chapters/{id}/reading-progress 테스트"""

    def test_record_reading_requires_auth(self) -> None:
        """인증 없이 접근 불가"""
        client = APIClient()
        chapter = baker.make("contents.Chapter")
        url = f"/api/v1/chapters/{chapter.id}/reading-progress/"

        response = client.post(url, {"progress": 0.5})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_record_reading(self) -> None:
        """읽은 기록 저장"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        client = APIClient()
        client.force_authenticate(user=user)
        url = f"/api/v1/chapters/{chapter.id}/reading-progress/"

        response = client.post(url, {"progress": 0.5})

        assert response.status_code == status.HTTP_200_OK
        log = ReadingLog.objects.get(user=user, chapter=chapter)
        assert float(log.progress) == 0.5

    def test_record_reading_marks_completed(self) -> None:
        """진행률 1.0이면 완독"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        client = APIClient()
        client.force_authenticate(user=user)
        url = f"/api/v1/chapters/{chapter.id}/reading-progress/"

        response = client.post(url, {"progress": 1.0})

        assert response.status_code == status.HTTP_200_OK
        log = ReadingLog.objects.get(user=user, chapter=chapter)
        assert log.is_completed is True
