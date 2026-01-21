"""
Tests for draft auto-save endpoint in ChapterViewSet.
POST /api/v1/branches/{branch_id}/chapters/draft/
"""

from unittest.mock import patch

import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.novels.models import Branch
from apps.users.models import User
from apps.contents.models import Chapter


def get_tokens_for_user(user):
    """
    주어진 사용자에 대해 JWT 액세스 토큰과 리프레시 토큰을 생성합니다.
    
    Parameters:
        user (django.contrib.auth.models.User): 토큰을 발급할 대상 사용자 객체.
    
    Returns:
        dict: "access" 키에 액세스 토큰 문자열을, "refresh" 키에 리프레시 토큰 문자열을 담은 딕셔너리.
    """
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


@pytest.mark.django_db
class TestChapterDraft:
    """Tests for POST /api/v1/branches/{branch_id}/chapters/draft/"""

    def test_save_draft_success(self):
        """
        초안 자동저장 엔드포인트에 대해 정상적으로 초안을 저장하는 동작을 검증한다.
        
        인증된 사용자로 브랜치에 제목과 내용을 POST하면 HTTP 200 응답과 성공 플래그를 반환하고,
        DraftService.save_draft가 branch_id에 브랜치 id와 chapter_id=None, 전달한 title과 content로 한 번 호출되는지 확인한다.
        """
        user = baker.make(User)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        branch = baker.make(Branch, author=user)

        url = f"/api/v1/branches/{branch.id}/chapters/draft/"
        data = {
            "title": "Draft Title",
            "content": "Draft Content",
        }

        with patch("apps.contents.views.DraftService") as MockDraftService:
            mock_service = MockDraftService.return_value
            response = client.post(url, data, format="json")

            assert response.status_code == status.HTTP_200_OK
            assert response.json()["success"] is True

            mock_service.save_draft.assert_called_once_with(
                branch_id=branch.id,
                chapter_id=None,
                title="Draft Title",
                content="Draft Content",
            )

    def test_save_draft_with_chapter_id(self):
        """
        기존 챕터의 드래프트를 저장(업데이트)하는 동작을 검증한다.
        
        요청에 `chapter_id`가 포함되었을 때 `DraftService.save_draft`가 해당 `chapter_id`, 제목 및 내용을 사용해 호출되는지 확인한다.
        """
        user = baker.make(User)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        branch = baker.make(Branch, author=user)
        chapter = baker.make(Chapter, branch=branch)

        url = f"/api/v1/branches/{branch.id}/chapters/draft/"
        data = {
            "title": "Updated Draft",
            "content": "Updated Content",
            "chapter_id": chapter.id,
        }

        with patch("apps.contents.views.DraftService") as MockDraftService:
            mock_service = MockDraftService.return_value
            response = client.post(url, data, format="json")

            assert response.status_code == status.HTTP_200_OK
            mock_service.save_draft.assert_called_once_with(
                branch_id=branch.id,
                chapter_id=chapter.id,
                title="Updated Draft",
                content="Updated Content",
            )

    def test_save_draft_unauthorized(self):
        """Non-author should not be able to save draft."""
        owner = baker.make(User)
        other_user = baker.make(User)
        client = APIClient()
        tokens = get_tokens_for_user(other_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        branch = baker.make(Branch, author=owner)

        url = f"/api/v1/branches/{branch.id}/chapters/draft/"
        data = {"title": "Draft", "content": "Content"}

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_save_draft_validation_error(self):
        """Should fail if content is missing."""
        user = baker.make(User)
        client = APIClient()
        tokens = get_tokens_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        branch = baker.make(Branch, author=user)
        url = f"/api/v1/branches/{branch.id}/chapters/draft/"

        # Missing content
        data = {"title": "Draft Title"}

        # NOTE: The implementation should probably require content,
        # but the task description says "Or allow empty content?".
        # Let's assume content is required for now as it's the main thing.
        # But wait, the task says: "Verify 400 if validation fails (e.g. missing content?). Or allow empty content?"
        # I'll enforce content presence for now, or at least the key.

        response = client.post(url, data, format="json")
        # If I use a serializer or manual check, this should be 400.
        # Since I haven't implemented it yet, I'll expect 400 and implement validation.
        assert response.status_code == status.HTTP_400_BAD_REQUEST