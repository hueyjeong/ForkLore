"""
ChapterViewSet Tests - TDD approach for Chapter API endpoints.

Tests:
- GET /api/v1/branches/{branch_id}/chapters - List chapters
- GET /api/v1/branches/{branch_id}/chapters/{chapter_number} - Get chapter detail
- POST /api/v1/branches/{branch_id}/chapters - Create chapter
- PATCH /api/v1/chapters/{id} - Update chapter
- POST /api/v1/chapters/{id}/publish - Publish chapter
- POST /api/v1/chapters/{id}/schedule - Schedule chapter
- DELETE /api/v1/chapters/{id} - Delete chapter
"""

from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.contents.models import Chapter, ChapterStatus
from apps.novels.models import Branch
from apps.users.models import User


def get_tokens_for_user(user: User) -> dict[str, str]:
    """Generate JWT tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


@pytest.mark.django_db
class TestChapterList:
    """Tests for GET /api/v1/branches/{branch_id}/chapters"""

    def test_list_chapters_for_branch(self) -> None:
        """Should return all published chapters for a branch."""
        client = APIClient()
        branch = baker.make(Branch)
        baker.make(
            Chapter,
            branch=branch,
            chapter_number=1,
            title="Chapter 1",
            status=ChapterStatus.PUBLISHED,
        )
        baker.make(
            Chapter,
            branch=branch,
            chapter_number=2,
            title="Chapter 2",
            status=ChapterStatus.PUBLISHED,
        )
        # Draft should not appear
        baker.make(
            Chapter,
            branch=branch,
            chapter_number=3,
            status=ChapterStatus.DRAFT,
        )

        url = f"/api/v1/branches/{branch.id}/chapters/"
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["results"]) == 2

    def test_list_chapters_ordered_by_number(self) -> None:
        """Should return chapters ordered by chapter_number."""
        client = APIClient()
        branch = baker.make(Branch)
        baker.make(Chapter, branch=branch, chapter_number=3, status=ChapterStatus.PUBLISHED)
        baker.make(Chapter, branch=branch, chapter_number=1, status=ChapterStatus.PUBLISHED)
        baker.make(Chapter, branch=branch, chapter_number=2, status=ChapterStatus.PUBLISHED)

        url = f"/api/v1/branches/{branch.id}/chapters/"
        response = client.get(url)

        data = response.json()
        results = data["data"]["results"]
        assert results[0]["chapterNumber"] == 1
        assert results[1]["chapterNumber"] == 2
        assert results[2]["chapterNumber"] == 3

    def test_author_can_see_all_chapters(self) -> None:
        """Branch author should see drafts too."""
        user = baker.make(User)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        branch = baker.make(Branch, author=user)
        baker.make(Chapter, branch=branch, chapter_number=1, status=ChapterStatus.PUBLISHED)
        baker.make(Chapter, branch=branch, chapter_number=2, status=ChapterStatus.DRAFT)

        url = f"/api/v1/branches/{branch.id}/chapters/"
        response = client.get(url)

        data = response.json()
        assert len(data["data"]["results"]) == 2


@pytest.mark.django_db
class TestChapterDetail:
    """Tests for GET /api/v1/branches/{branch_id}/chapters/{chapter_number}"""

    def test_get_chapter_detail(self) -> None:
        """Should return chapter detail with HTML content."""
        client = APIClient()
        branch = baker.make(Branch)
        chapter = baker.make(
            Chapter,
            branch=branch,
            chapter_number=1,
            title="Test Chapter",
            content_html="<p>Hello</p>",
            status=ChapterStatus.PUBLISHED,
        )

        url = f"/api/v1/branches/{branch.id}/chapters/{chapter.chapter_number}/"
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["title"] == "Test Chapter"
        assert data["data"]["contentHtml"] == "<p>Hello</p>"

    def test_get_nonexistent_chapter_returns_404(self) -> None:
        """Should return 404 for non-existent chapter."""
        client = APIClient()
        branch = baker.make(Branch)

        url = f"/api/v1/branches/{branch.id}/chapters/999/"
        response = client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestChapterCreate:
    """Tests for POST /api/v1/branches/{branch_id}/chapters"""

    def test_create_chapter_as_author(self) -> None:
        """Branch author should be able to create chapters."""
        user = baker.make(User)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        branch = baker.make(Branch, author=user)

        url = f"/api/v1/branches/{branch.id}/chapters/"
        data = {
            "title": "New Chapter",
            "content": "# Hello World\n\nThis is content.",
        }
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert resp_data["success"] is True
        assert resp_data["data"]["title"] == "New Chapter"
        assert resp_data["data"]["chapterNumber"] == 1
        assert resp_data["data"]["status"] == ChapterStatus.DRAFT

    def test_create_chapter_unauthenticated(self) -> None:
        """Unauthenticated user should not create chapters."""
        client = APIClient()
        branch = baker.make(Branch)

        url = f"/api/v1/branches/{branch.id}/chapters/"
        data = {"title": "New Chapter", "content": "Content"}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_chapter_non_author(self) -> None:
        """Non-author should not create chapters in others' branches."""
        owner = baker.make(User)
        other_user = baker.make(User)
        client = APIClient()
        tokens = get_tokens_for_user(other_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        branch = baker.make(Branch, author=owner)

        url = f"/api/v1/branches/{branch.id}/chapters/"
        data = {"title": "New Chapter", "content": "Content"}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestChapterUpdate:
    """Tests for PATCH /api/v1/chapters/{id}"""

    def test_update_draft_chapter(self) -> None:
        """Author should be able to update their draft chapter."""
        user = baker.make(User)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        branch = baker.make(Branch, author=user)
        chapter = baker.make(Chapter, branch=branch, title="Old Title", status=ChapterStatus.DRAFT)

        url = f"/api/v1/chapters/{chapter.id}/"
        data = {"title": "New Title"}
        response = client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["data"]["title"] == "New Title"


@pytest.mark.django_db
class TestChapterPublish:
    """Tests for POST /api/v1/chapters/{id}/publish"""

    def test_publish_draft_chapter(self) -> None:
        """Author should be able to publish their draft chapter."""
        user = baker.make(User)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        branch = baker.make(Branch, author=user, chapter_count=0)
        chapter = baker.make(Chapter, branch=branch, status=ChapterStatus.DRAFT)

        url = f"/api/v1/chapters/{chapter.id}/publish/"
        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["data"]["status"] == ChapterStatus.PUBLISHED
        assert resp_data["data"]["publishedAt"] is not None


@pytest.mark.django_db
class TestChapterSchedule:
    """Tests for POST /api/v1/chapters/{id}/schedule"""

    def test_schedule_chapter(self) -> None:
        """Author should be able to schedule their draft chapter."""
        user = baker.make(User)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        branch = baker.make(Branch, author=user)
        chapter = baker.make(Chapter, branch=branch, status=ChapterStatus.DRAFT)
        future_time = timezone.now() + timedelta(days=1)

        url = f"/api/v1/chapters/{chapter.id}/schedule/"
        data = {"scheduled_at": future_time.isoformat()}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["data"]["status"] == ChapterStatus.SCHEDULED


@pytest.mark.django_db
class TestChapterDelete:
    """Tests for DELETE /api/v1/chapters/{id}"""

    def test_delete_chapter(self) -> None:
        """Author should be able to delete their chapter."""
        user = baker.make(User)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        branch = baker.make(Branch, author=user)
        chapter = baker.make(Chapter, branch=branch)

        url = f"/api/v1/chapters/{chapter.id}/"
        response = client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Chapter.objects.filter(id=chapter.id).exists()
