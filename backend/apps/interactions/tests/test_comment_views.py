"""
TDD: Comment/Like ViewSet 테스트
RED → GREEN → REFACTOR
"""

import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from apps.interactions.models import Comment

pytestmark = pytest.mark.django_db


class TestCommentListView:
    """GET /api/v1/chapters/{id}/comments 테스트"""

    def test_list_comments(self) -> None:
        """댓글 목록 조회"""
        chapter = baker.make("contents.Chapter")
        baker.make("interactions.Comment", chapter=chapter, _quantity=3)

        client = APIClient()
        url = f"/api/v1/chapters/{chapter.id}/comments/"

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_list_comments_by_paragraph(self) -> None:
        """문단별 댓글 필터링"""
        chapter = baker.make("contents.Chapter")
        baker.make("interactions.Comment", chapter=chapter, paragraph_index=3, _quantity=2)
        baker.make("interactions.Comment", chapter=chapter, paragraph_index=5)

        client = APIClient()
        url = f"/api/v1/chapters/{chapter.id}/comments/?paragraph_index=3"

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2


class TestCommentCreateView:
    """POST /api/v1/chapters/{id}/comments 테스트"""

    def test_create_comment_requires_auth(self) -> None:
        """인증 없이 댓글 작성 불가"""
        chapter = baker.make("contents.Chapter")
        client = APIClient()
        url = f"/api/v1/chapters/{chapter.id}/comments/"

        response = client.post(url, {"content": "테스트"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_comment(self) -> None:
        """댓글 작성"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        client = APIClient()
        client.force_authenticate(user=user)
        url = f"/api/v1/chapters/{chapter.id}/comments/"

        response = client.post(url, {"content": "테스트 댓글입니다."})

        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.filter(chapter=chapter, user=user).exists()

    def test_create_paragraph_comment(self) -> None:
        """문단 댓글 작성"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        client = APIClient()
        client.force_authenticate(user=user)
        url = f"/api/v1/chapters/{chapter.id}/comments/"

        response = client.post(
            url,
            {
                "content": "문단 댓글",
                "paragraph_index": 3,
                "selection_start": 10,
                "selection_end": 50,
                "quoted_text": "인용문",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["paragraph_index"] == 3


class TestCommentUpdateView:
    """PATCH /api/v1/comments/{id} 테스트"""

    def test_update_comment(self) -> None:
        """댓글 수정"""
        user = baker.make("users.User")
        comment = baker.make("interactions.Comment", user=user, content="원본")

        client = APIClient()
        client.force_authenticate(user=user)
        url = f"/api/v1/comments/{comment.id}/"

        response = client.patch(url, {"content": "수정됨"})

        assert response.status_code == status.HTTP_200_OK
        comment.refresh_from_db()
        assert comment.content == "수정됨"

    def test_update_comment_not_owner(self) -> None:
        """작성자 아니면 수정 불가"""
        user1 = baker.make("users.User")
        user2 = baker.make("users.User")
        comment = baker.make("interactions.Comment", user=user1)

        client = APIClient()
        client.force_authenticate(user=user2)
        url = f"/api/v1/comments/{comment.id}/"

        response = client.patch(url, {"content": "수정 시도"})

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCommentDeleteView:
    """DELETE /api/v1/comments/{id} 테스트"""

    def test_delete_comment(self) -> None:
        """댓글 삭제"""
        user = baker.make("users.User")
        comment = baker.make("interactions.Comment", user=user)

        client = APIClient()
        client.force_authenticate(user=user)
        url = f"/api/v1/comments/{comment.id}/"

        response = client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        comment.refresh_from_db()
        assert comment.deleted_at is not None


class TestCommentPinView:
    """POST/DELETE /api/v1/comments/{id}/pin 테스트"""

    def test_pin_comment(self) -> None:
        """댓글 고정"""
        author = baker.make("users.User")
        branch = baker.make("novels.Branch", author=author)
        chapter = baker.make("contents.Chapter", branch=branch)
        comment = baker.make("interactions.Comment", chapter=chapter)

        client = APIClient()
        client.force_authenticate(user=author)
        url = f"/api/v1/comments/{comment.id}/pin/"

        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK
        comment.refresh_from_db()
        assert comment.is_pinned is True

    def test_unpin_comment(self) -> None:
        """댓글 고정 해제"""
        author = baker.make("users.User")
        branch = baker.make("novels.Branch", author=author)
        chapter = baker.make("contents.Chapter", branch=branch)
        comment = baker.make("interactions.Comment", chapter=chapter, is_pinned=True)

        client = APIClient()
        client.force_authenticate(user=author)
        url = f"/api/v1/comments/{comment.id}/pin/"

        response = client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        comment.refresh_from_db()
        assert comment.is_pinned is False


class TestLikeView:
    """POST/DELETE /api/v1/comments/{id}/like 테스트"""

    def test_like_comment(self) -> None:
        """댓글 좋아요"""
        user = baker.make("users.User")
        comment = baker.make("interactions.Comment", like_count=0)

        client = APIClient()
        client.force_authenticate(user=user)
        url = f"/api/v1/comments/{comment.id}/like/"

        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["liked"] is True
        comment.refresh_from_db()
        assert comment.like_count == 1

    def test_unlike_comment(self) -> None:
        """댓글 좋아요 취소"""
        user = baker.make("users.User")
        comment = baker.make("interactions.Comment", like_count=0)

        client = APIClient()
        client.force_authenticate(user=user)
        url = f"/api/v1/comments/{comment.id}/like/"

        # Like first
        client.post(url)
        # Unlike
        response = client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["liked"] is False
        comment.refresh_from_db()
        assert comment.like_count == 0

    def test_like_requires_auth(self) -> None:
        """좋아요는 인증 필요"""
        comment = baker.make("interactions.Comment")

        client = APIClient()
        url = f"/api/v1/comments/{comment.id}/like/"

        response = client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestChapterLikeView:
    """POST/DELETE /api/v1/chapters/{id}/like 테스트"""

    def test_like_chapter(self) -> None:
        """회차 좋아요"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        client = APIClient()
        client.force_authenticate(user=user)
        url = f"/api/v1/chapters/{chapter.id}/like/"

        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["liked"] is True
