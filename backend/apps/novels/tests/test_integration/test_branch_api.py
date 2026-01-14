"""
Integration tests for Branch API endpoints.
Tests branch forking, visibility, voting, and deletion logic.
"""

import json
from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.novels.models import Branch, Novel


def get_json(response: Response) -> Any:
    """Helper to parse JSON from response content."""
    return json.loads(response.content)


# =============================================================================
# Branch Management Tests
# =============================================================================


class TestBranchManagement:
    """Tests for Branch operations"""

    def test_fork_branch_copies_data(
        self, reader_client: APIClient, author: Any, reader: Any, db: Any
    ) -> None:
        """Forking a branch should copy its data to new branch."""
        # Create novel with main branch using NovelService
        from apps.novels.services import NovelService

        service = NovelService()
        novel = service.create(author=author, data={"title": "Test Novel", "genre": "FANTASY"})
        main_branch = Branch.objects.get(novel=novel, is_main=True)

        # Fork the main branch
        url = reverse("novel-branches-list", kwargs={"novel_pk": novel.pk})
        fork_data = {
            "name": "My Fork",
            "description": "Forked version",
            "parentBranchId": main_branch.pk,
        }
        response = reader_client.post(url, fork_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = get_json(response)
        assert data["success"] is True

        # Verify forked branch
        forked_branch = Branch.objects.get(author=reader, name="My Fork")
        assert forked_branch.parent_branch == main_branch
        assert forked_branch.novel == novel
        assert forked_branch.is_main is False

    def test_update_branch_visibility(self, author_client: APIClient, author: Any, db: Any) -> None:
        """Branch owner should be able to toggle visibility."""
        # Create branch
        novel = Novel.objects.create(author=author, title="Test Novel", genre="FANTASY")
        branch = Branch.objects.create(
            novel=novel,
            author=author,
            name="Test Branch",
            visibility="PRIVATE",
        )

        # Update visibility
        url = reverse("branch-visibility", kwargs={"pk": branch.pk})
        update_data = {"visibility": "PUBLIC"}
        response = author_client.patch(url, update_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        branch.refresh_from_db()
        assert branch.visibility == "PUBLIC"

    def test_cannot_delete_main_branch(
        self, author_client: APIClient, author: Any, db: Any
    ) -> None:
        """Main branch should not be deletable (delete not supported)."""
        from apps.novels.services import NovelService

        service = NovelService()
        novel = service.create(author=author, data={"title": "Test Novel", "genre": "FANTASY"})
        main_branch = Branch.objects.get(novel=novel, is_main=True)

        # Try to delete - should return 405 METHOD NOT ALLOWED
        url = reverse("branch-detail", kwargs={"pk": main_branch.pk})
        response = author_client.delete(url)

        # DELETE is not allowed on branch detail endpoint
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        # Main branch should still exist
        assert Branch.objects.filter(pk=main_branch.pk).exists()

    def test_vote_for_branch(
        self, reader_client: APIClient, author: Any, reader: Any, db: Any
    ) -> None:
        """User should be able to vote for a branch."""
        novel = Novel.objects.create(author=author, title="Test Novel", genre="FANTASY")
        branch = Branch.objects.create(
            novel=novel,
            author=author,
            name="Test Branch",
        )

        url = reverse("branch-vote", kwargs={"pk": branch.pk})
        response = reader_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        branch.refresh_from_db()
        assert branch.vote_count == 1

    def test_unvote_for_branch(
        self, reader_client: APIClient, author: Any, reader: Any, db: Any
    ) -> None:
        """User should be able to remove their vote."""
        from apps.novels.models import BranchVote

        novel = Novel.objects.create(author=author, title="Test Novel", genre="FANTASY")
        branch = Branch.objects.create(
            novel=novel,
            author=author,
            name="Test Branch",
        )

        # First vote
        url = reverse("branch-vote", kwargs={"pk": branch.pk})
        reader_client.post(url, {}, format="json")
        branch.refresh_from_db()
        vote_count_after_vote = branch.vote_count

        # Then unvote
        response = reader_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Verify vote was removed
        assert not BranchVote.objects.filter(branch=branch, user=reader).exists()
