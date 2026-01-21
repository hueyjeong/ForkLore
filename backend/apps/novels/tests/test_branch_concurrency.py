"""
Tests for Branch Optimistic Locking (Concurrency).
"""

import pytest
from model_bakery import baker

from apps.novels.models import Branch, Novel
from apps.novels.services import BranchService
from common.exceptions import ConflictError


@pytest.mark.django_db
class TestBranchConcurrency:
    """Tests for optimistic locking in Branch operations."""

    def test_fork_with_correct_version(self):
        """Should fork successfully when version matches."""
        service = BranchService()
        user = baker.make("users.User")
        novel = baker.make(Novel, allow_branching=True)
        parent_branch = baker.make(Branch, novel=novel, is_main=True, version=1)

        data = {
            "name": "Fork Test",
            "fork_point_chapter": 5,
        }

        # Fork with correct version
        forked_branch = service.fork(
            novel_id=novel.id,
            parent_branch_id=parent_branch.id,
            author=user,
            data=data,
            parent_version=1,
        )

        assert forked_branch is not None
        assert forked_branch.parent_branch == parent_branch

    def test_fork_with_incorrect_version(self):
        """Should raise ConflictError when version mismatches."""
        service = BranchService()
        user = baker.make("users.User")
        novel = baker.make(Novel, allow_branching=True)
        parent_branch = baker.make(Branch, novel=novel, is_main=True, version=2)

        data = {
            "name": "Fork Test",
            "fork_point_chapter": 5,
        }

        # Fork with incorrect version (1 != 2)
        with pytest.raises(ConflictError):
            service.fork(
                novel_id=novel.id,
                parent_branch_id=parent_branch.id,
                author=user,
                data=data,
                parent_version=1,
            )

    def test_update_increments_version(self):
        """Should increment version on update."""
        service = BranchService()
        user = baker.make("users.User")
        branch = baker.make(Branch, author=user, version=1)

        updated_branch = service.update(
            branch_id=branch.id,
            author=user,
            data={"name": "Updated Name"},
        )

        assert updated_branch.version == 2
        assert updated_branch.name == "Updated Name"

    def test_update_visibility_increments_version(self):
        """Should increment version on visibility update."""
        service = BranchService()
        user = baker.make("users.User")
        branch = baker.make(Branch, author=user, version=1, is_main=False)

        updated_branch = service.update_visibility(
            branch_id=branch.id,
            author=user,
            visibility="PUBLIC",
        )

        assert updated_branch.version == 2
        assert updated_branch.visibility == "PUBLIC"

    def test_vote_does_not_increment_version(self):
        """Test voting does NOT increment version (to avoid conflicts)"""
        service = BranchService()
        user = baker.make("users.User")
        branch = baker.make(Branch, version=1, vote_count=0)

        service.vote(branch_id=branch.id, user=user)

        branch.refresh_from_db()
        assert branch.version == 1  # Should NOT increment
        assert branch.vote_count == 1

    def test_unvote_does_not_increment_version(self):
        """Test unvoting does NOT increment version"""
        service = BranchService()
        user = baker.make("users.User")
        branch = baker.make(Branch, version=1, vote_count=1)
        baker.make("novels.BranchVote", user=user, branch=branch)

        service.unvote(branch_id=branch.id, user=user)

        branch.refresh_from_db()
        assert branch.version == 1  # Should NOT increment
        assert branch.vote_count == 0
