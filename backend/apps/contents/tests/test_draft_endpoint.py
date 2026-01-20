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
    """Generate JWT tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


@pytest.mark.django_db
class TestChapterDraft:
    """Tests for POST /api/v1/branches/{branch_id}/chapters/draft/"""

    def test_save_draft_success(self):
        """Should save draft successfully."""
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
        """Should save draft for existing chapter."""
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
