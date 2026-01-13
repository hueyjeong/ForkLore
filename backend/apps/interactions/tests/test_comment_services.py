"""
TDD: CommentService, LikeService 테스트
RED → GREEN → REFACTOR
"""

import pytest
from django.core.exceptions import ValidationError
from model_bakery import baker

from apps.interactions.services import CommentService, LikeService
from apps.interactions.models import Comment, Like


pytestmark = pytest.mark.django_db


# =============================================================================
# CommentService Tests
# =============================================================================


class TestCommentServiceCreate:
    """CommentService.create() 테스트"""

    def test_create_comment(self):
        """댓글 생성"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        comment = CommentService.create(
            user=user,
            chapter_id=chapter.id,
            content="테스트 댓글입니다.",
        )

        assert comment.id is not None
        assert comment.user == user
        assert comment.chapter == chapter
        assert comment.content == "테스트 댓글입니다."

    def test_create_reply(self):
        """대댓글 생성"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")
        parent = baker.make("interactions.Comment", chapter=chapter)

        reply = CommentService.create(
            user=user,
            chapter_id=chapter.id,
            content="대댓글입니다.",
            parent_id=parent.id,
        )

        assert reply.parent == parent

    def test_create_paragraph_comment(self):
        """문단 댓글 생성"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        comment = CommentService.create(
            user=user,
            chapter_id=chapter.id,
            content="문단 댓글",
            paragraph_index=3,
            selection_start=10,
            selection_end=50,
            quoted_text="인용된 텍스트",
        )

        assert comment.paragraph_index == 3
        assert comment.selection_start == 10
        assert comment.selection_end == 50
        assert comment.quoted_text == "인용된 텍스트"

    def test_create_comment_invalid_selection(self):
        """selection_start >= selection_end 시 에러"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        with pytest.raises(ValueError):
            CommentService.create(
                user=user,
                chapter_id=chapter.id,
                content="잘못된 선택",
                selection_start=50,
                selection_end=10,
            )


class TestCommentServiceUpdate:
    """CommentService.update() 테스트"""

    def test_update_comment(self):
        """댓글 수정"""
        user = baker.make("users.User")
        comment = baker.make("interactions.Comment", user=user, content="원본")

        updated = CommentService.update(
            comment_id=comment.id,
            user=user,
            content="수정됨",
        )

        assert updated.content == "수정됨"

    def test_update_comment_not_owner(self):
        """작성자 아니면 수정 불가"""
        user1 = baker.make("users.User")
        user2 = baker.make("users.User")
        comment = baker.make("interactions.Comment", user=user1)

        with pytest.raises(PermissionError):
            CommentService.update(
                comment_id=comment.id,
                user=user2,
                content="수정 시도",
            )


class TestCommentServiceDelete:
    """CommentService.delete() 테스트"""

    def test_delete_comment_soft(self):
        """댓글 소프트 삭제"""
        user = baker.make("users.User")
        comment = baker.make("interactions.Comment", user=user)

        CommentService.delete(comment_id=comment.id, user=user)

        comment.refresh_from_db()
        assert comment.deleted_at is not None

    def test_delete_comment_not_owner(self):
        """작성자 아니면 삭제 불가"""
        user1 = baker.make("users.User")
        user2 = baker.make("users.User")
        comment = baker.make("interactions.Comment", user=user1)

        with pytest.raises(PermissionError):
            CommentService.delete(comment_id=comment.id, user=user2)


class TestCommentServiceList:
    """CommentService.list() 테스트"""

    def test_list_comments_by_chapter(self):
        """회차별 댓글 목록"""
        chapter = baker.make("contents.Chapter")
        baker.make("interactions.Comment", chapter=chapter, _quantity=3)
        baker.make("interactions.Comment")  # 다른 회차

        comments = CommentService.list(chapter_id=chapter.id)

        assert len(comments) == 3

    def test_list_comments_by_paragraph(self):
        """문단별 댓글 목록"""
        chapter = baker.make("contents.Chapter")
        baker.make("interactions.Comment", chapter=chapter, paragraph_index=3, _quantity=2)
        baker.make("interactions.Comment", chapter=chapter, paragraph_index=5)

        comments = CommentService.list(chapter_id=chapter.id, paragraph_index=3)

        assert len(comments) == 2

    def test_list_excludes_deleted(self):
        """소프트 삭제된 댓글 제외"""
        chapter = baker.make("contents.Chapter")
        user = baker.make("users.User")
        comment = baker.make("interactions.Comment", chapter=chapter, user=user)
        baker.make("interactions.Comment", chapter=chapter)

        CommentService.delete(comment_id=comment.id, user=user)

        comments = CommentService.list(chapter_id=chapter.id)

        assert len(comments) == 1


class TestCommentServicePin:
    """CommentService.pin/unpin() 테스트"""

    def test_pin_comment_by_author(self):
        """작가가 댓글 고정"""
        author = baker.make("users.User")
        branch = baker.make("novels.Branch", author=author)
        chapter = baker.make("contents.Chapter", branch=branch)
        comment = baker.make("interactions.Comment", chapter=chapter)

        pinned = CommentService.pin(comment_id=comment.id, user=author)

        assert pinned.is_pinned is True

    def test_pin_comment_not_author(self):
        """작가 아니면 고정 불가"""
        author = baker.make("users.User")
        other = baker.make("users.User")
        branch = baker.make("novels.Branch", author=author)
        chapter = baker.make("contents.Chapter", branch=branch)
        comment = baker.make("interactions.Comment", chapter=chapter)

        with pytest.raises(PermissionError):
            CommentService.pin(comment_id=comment.id, user=other)

    def test_unpin_comment(self):
        """댓글 고정 해제"""
        author = baker.make("users.User")
        branch = baker.make("novels.Branch", author=author)
        chapter = baker.make("contents.Chapter", branch=branch)
        comment = baker.make("interactions.Comment", chapter=chapter, is_pinned=True)

        unpinned = CommentService.unpin(comment_id=comment.id, user=author)

        assert unpinned.is_pinned is False


# =============================================================================
# LikeService Tests
# =============================================================================


class TestLikeServiceToggle:
    """LikeService.toggle() 테스트"""

    def test_like_comment(self):
        """댓글 좋아요"""
        user = baker.make("users.User")
        comment = baker.make("interactions.Comment")

        result = LikeService.toggle(user=user, target=comment)

        assert result["liked"] is True
        assert Like.objects.filter(user=user).count() == 1

    def test_unlike_comment(self):
        """댓글 좋아요 취소"""
        user = baker.make("users.User")
        comment = baker.make("interactions.Comment")

        # 첫 번째 토글: 좋아요
        LikeService.toggle(user=user, target=comment)
        # 두 번째 토글: 취소
        result = LikeService.toggle(user=user, target=comment)

        assert result["liked"] is False
        assert Like.objects.filter(user=user).count() == 0

    def test_like_chapter(self):
        """회차 좋아요"""
        user = baker.make("users.User")
        chapter = baker.make("contents.Chapter")

        result = LikeService.toggle(user=user, target=chapter)

        assert result["liked"] is True

    def test_like_updates_like_count(self):
        """좋아요 시 like_count 업데이트"""
        user = baker.make("users.User")
        comment = baker.make("interactions.Comment", like_count=0)

        LikeService.toggle(user=user, target=comment)

        comment.refresh_from_db()
        assert comment.like_count == 1

    def test_unlike_updates_like_count(self):
        """좋아요 취소 시 like_count 업데이트"""
        user = baker.make("users.User")
        comment = baker.make("interactions.Comment", like_count=0)

        # Like first
        LikeService.toggle(user=user, target=comment)
        comment.refresh_from_db()
        assert comment.like_count == 1

        # Unlike
        LikeService.toggle(user=user, target=comment)
        comment.refresh_from_db()
        assert comment.like_count == 0


class TestLikeServiceGetLikeStatus:
    """LikeService.get_like_status() 테스트"""

    def test_get_like_status_liked(self):
        """좋아요 상태 조회 - 좋아요함"""
        user = baker.make("users.User")
        comment = baker.make("interactions.Comment")
        LikeService.toggle(user=user, target=comment)

        status = LikeService.get_like_status(user=user, target=comment)

        assert status is True

    def test_get_like_status_not_liked(self):
        """좋아요 상태 조회 - 좋아요 안함"""
        user = baker.make("users.User")
        comment = baker.make("interactions.Comment")

        status = LikeService.get_like_status(user=user, target=comment)

        assert status is False
