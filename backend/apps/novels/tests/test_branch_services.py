"""
BranchService Tests - TDD approach for Branch system.

Tests:
- fork(): Create a forked branch from parent
- list(): List branches for a novel
- retrieve(): Get single branch by ID
- update_visibility(): Change branch visibility
- vote() / unvote(): Add/remove votes
"""

import pytest
from django.db import IntegrityError
from model_bakery import baker

from apps.novels.models import (
    Novel,
    Branch,
    BranchType,
    BranchVisibility,
    CanonStatus,
    BranchVote,
)
from apps.novels.services import BranchService


@pytest.mark.django_db
class TestBranchServiceList:
    """Tests for BranchService.list()"""

    def test_list_branches_for_novel(self):
        """Should return all non-deleted branches for a novel."""
        service = BranchService()
        novel = baker.make(Novel)
        main_branch = baker.make(
            Branch, novel=novel, is_main=True, visibility=BranchVisibility.PUBLIC
        )
        branch1 = baker.make(Branch, novel=novel, is_main=False, visibility=BranchVisibility.LINKED)
        branch2 = baker.make(Branch, novel=novel, is_main=False, visibility=BranchVisibility.PUBLIC)

        result = service.list(novel_id=novel.id)

        assert result.count() == 3
        assert main_branch in result
        assert branch1 in result
        assert branch2 in result

    def test_list_branches_excludes_deleted(self):
        """Should exclude soft-deleted branches."""
        service = BranchService()
        novel = baker.make(Novel)
        active_branch = baker.make(Branch, novel=novel, is_main=True)
        deleted_branch = baker.make(Branch, novel=novel, is_main=False)
        deleted_branch.soft_delete()

        result = service.list(novel_id=novel.id)

        assert result.count() == 1
        assert active_branch in result

    def test_list_branches_filter_by_visibility(self):
        """Should filter branches by visibility."""
        service = BranchService()
        novel = baker.make(Novel)
        baker.make(Branch, novel=novel, visibility=BranchVisibility.PUBLIC)
        linked_branch = baker.make(Branch, novel=novel, visibility=BranchVisibility.LINKED)
        baker.make(Branch, novel=novel, visibility=BranchVisibility.PRIVATE)

        result = service.list(novel_id=novel.id, visibility=BranchVisibility.LINKED)

        assert result.count() == 1
        assert linked_branch in result

    def test_list_branches_sort_by_votes(self):
        """Should sort branches by vote_count descending."""
        service = BranchService()
        novel = baker.make(Novel)
        low_votes = baker.make(Branch, novel=novel, vote_count=10)
        high_votes = baker.make(Branch, novel=novel, vote_count=100)
        mid_votes = baker.make(Branch, novel=novel, vote_count=50)

        result = service.list(novel_id=novel.id, sort="votes")

        result_list = list(result)
        assert result_list[0] == high_votes
        assert result_list[1] == mid_votes
        assert result_list[2] == low_votes

    def test_list_branches_sort_by_latest(self):
        """Should sort branches by created_at descending (default)."""
        service = BranchService()
        novel = baker.make(Novel)
        branch1 = baker.make(Branch, novel=novel)
        branch2 = baker.make(Branch, novel=novel)
        branch3 = baker.make(Branch, novel=novel)

        result = service.list(novel_id=novel.id, sort="latest")

        result_list = list(result)
        assert result_list[0] == branch3
        assert result_list[1] == branch2
        assert result_list[2] == branch1


@pytest.mark.django_db
class TestBranchServiceRetrieve:
    """Tests for BranchService.retrieve()"""

    def test_retrieve_branch_success(self):
        """Should return branch by ID."""
        service = BranchService()
        branch = baker.make(Branch)

        result = service.retrieve(branch_id=branch.id)

        assert result == branch

    def test_retrieve_deleted_branch_raises_error(self):
        """Should raise DoesNotExist for deleted branch."""
        service = BranchService()
        branch = baker.make(Branch)
        branch.soft_delete()

        with pytest.raises(Branch.DoesNotExist):
            service.retrieve(branch_id=branch.id)

    def test_retrieve_nonexistent_branch_raises_error(self):
        """Should raise DoesNotExist for invalid ID."""
        service = BranchService()

        with pytest.raises(Branch.DoesNotExist):
            service.retrieve(branch_id=99999)


@pytest.mark.django_db
class TestBranchServiceGetMainBranch:
    """Tests for BranchService.get_main_branch()"""

    def test_get_main_branch_success(self):
        """Should return the main branch of a novel."""
        service = BranchService()
        novel = baker.make(Novel)
        main_branch = baker.make(Branch, novel=novel, is_main=True)
        baker.make(Branch, novel=novel, is_main=False)

        result = service.get_main_branch(novel_id=novel.id)

        assert result == main_branch

    def test_get_main_branch_not_found(self):
        """Should raise DoesNotExist if no main branch."""
        service = BranchService()
        novel = baker.make(Novel)

        with pytest.raises(Branch.DoesNotExist):
            service.get_main_branch(novel_id=novel.id)


@pytest.mark.django_db
class TestBranchServiceFork:
    """Tests for BranchService.fork()"""

    def test_fork_branch_success(self):
        """Should create a forked branch from parent."""
        service = BranchService()
        user = baker.make("users.User")
        novel = baker.make(Novel, allow_branching=True)
        parent_branch = baker.make(Branch, novel=novel, is_main=True)

        data = {
            "name": "IF: 다른 선택",
            "description": "만약 주인공이 다른 선택을 했다면...",
            "branch_type": BranchType.IF_STORY,
            "fork_point_chapter": 15,
        }

        result = service.fork(
            novel_id=novel.id,
            parent_branch_id=parent_branch.id,
            author=user,
            data=data,
        )

        assert result.novel == novel
        assert result.author == user
        assert result.parent_branch == parent_branch
        assert result.name == "IF: 다른 선택"
        assert result.branch_type == BranchType.IF_STORY
        assert result.fork_point_chapter == 15
        assert result.is_main is False
        assert result.visibility == BranchVisibility.PRIVATE

    def test_fork_branch_increments_novel_branch_count(self):
        """Should increment novel's branch_count when forking."""
        service = BranchService()
        user = baker.make("users.User")
        novel = baker.make(Novel, allow_branching=True, branch_count=1)
        parent_branch = baker.make(Branch, novel=novel, is_main=True)

        service.fork(
            novel_id=novel.id,
            parent_branch_id=parent_branch.id,
            author=user,
            data={"name": "Fork Test", "branch_type": BranchType.FAN_FIC},
        )

        novel.refresh_from_db()
        assert novel.branch_count == 2

    def test_fork_branch_not_allowed_raises_error(self):
        """Should raise error if novel doesn't allow branching."""
        service = BranchService()
        user = baker.make("users.User")
        novel = baker.make(Novel, allow_branching=False)
        parent_branch = baker.make(Branch, novel=novel, is_main=True)

        with pytest.raises(PermissionError) as exc_info:
            service.fork(
                novel_id=novel.id,
                parent_branch_id=parent_branch.id,
                author=user,
                data={"name": "Test", "branch_type": BranchType.FAN_FIC},
            )

        assert "브랜치 생성이 허용되지 않습니다" in str(exc_info.value)

    def test_fork_requires_name(self):
        """Should raise error if name is missing."""
        service = BranchService()
        user = baker.make("users.User")
        novel = baker.make(Novel, allow_branching=True)
        parent_branch = baker.make(Branch, novel=novel, is_main=True)

        with pytest.raises(ValueError) as exc_info:
            service.fork(
                novel_id=novel.id,
                parent_branch_id=parent_branch.id,
                author=user,
                data={"branch_type": BranchType.FAN_FIC},
            )

        assert "이름은 필수입니다" in str(exc_info.value)


@pytest.mark.django_db
class TestBranchServiceUpdateVisibility:
    """Tests for BranchService.update_visibility()"""

    def test_update_visibility_success(self):
        """Should update branch visibility."""
        service = BranchService()
        user = baker.make("users.User")
        branch = baker.make(Branch, author=user, visibility=BranchVisibility.PRIVATE, is_main=False)

        result = service.update_visibility(
            branch_id=branch.id,
            author=user,
            visibility=BranchVisibility.PUBLIC,
        )

        assert result.visibility == BranchVisibility.PUBLIC

    def test_update_visibility_not_owner_raises_error(self):
        """Should raise PermissionError if not the owner."""
        service = BranchService()
        owner = baker.make("users.User")
        other_user = baker.make("users.User")
        branch = baker.make(Branch, author=owner, visibility=BranchVisibility.PRIVATE)

        with pytest.raises(PermissionError) as exc_info:
            service.update_visibility(
                branch_id=branch.id,
                author=other_user,
                visibility=BranchVisibility.PUBLIC,
            )

        assert "권한이 없습니다" in str(exc_info.value)

    def test_update_visibility_main_branch_raises_error(self):
        """Should raise error when trying to change main branch visibility."""
        service = BranchService()
        user = baker.make("users.User")
        branch = baker.make(Branch, author=user, is_main=True, visibility=BranchVisibility.PUBLIC)

        with pytest.raises(ValueError) as exc_info:
            service.update_visibility(
                branch_id=branch.id,
                author=user,
                visibility=BranchVisibility.PRIVATE,
            )

        assert "메인 브랜치" in str(exc_info.value)


@pytest.mark.django_db
class TestBranchServiceVote:
    """Tests for BranchService.vote() and unvote()"""

    def test_vote_success(self):
        """Should create a vote for a branch."""
        service = BranchService()
        user = baker.make("users.User")
        branch = baker.make(Branch, vote_count=0)

        result = service.vote(branch_id=branch.id, user=user)

        assert result is True
        assert BranchVote.objects.filter(user=user, branch=branch).exists()
        branch.refresh_from_db()
        assert branch.vote_count == 1

    def test_vote_duplicate_raises_error(self):
        """Should raise error for duplicate vote."""
        service = BranchService()
        user = baker.make("users.User")
        branch = baker.make(Branch, vote_count=1)
        baker.make(BranchVote, user=user, branch=branch)

        with pytest.raises(IntegrityError):
            service.vote(branch_id=branch.id, user=user)

    def test_unvote_success(self):
        """Should remove a vote from a branch."""
        service = BranchService()
        user = baker.make("users.User")
        branch = baker.make(Branch, vote_count=1)
        baker.make(BranchVote, user=user, branch=branch)

        result = service.unvote(branch_id=branch.id, user=user)

        assert result is True
        assert not BranchVote.objects.filter(user=user, branch=branch).exists()
        branch.refresh_from_db()
        assert branch.vote_count == 0

    def test_unvote_not_voted_returns_false(self):
        """Should return False if user hasn't voted."""
        service = BranchService()
        user = baker.make("users.User")
        branch = baker.make(Branch, vote_count=0)

        result = service.unvote(branch_id=branch.id, user=user)

        assert result is False

    def test_vote_count_cannot_go_negative(self):
        """Vote count should not go below 0."""
        service = BranchService()
        user = baker.make("users.User")
        branch = baker.make(Branch, vote_count=0)
        baker.make(BranchVote, user=user, branch=branch)

        service.unvote(branch_id=branch.id, user=user)

        branch.refresh_from_db()
        assert branch.vote_count == 0
