"""
BranchViewSet Tests - TDD approach for Branch API endpoints.

Tests:
- GET /novels/{id}/branches - List branches
- GET /novels/{id}/branches/main - Get main branch
- GET /branches/{id} - Retrieve branch
- POST /novels/{id}/branches - Fork branch
- PATCH /branches/{id}/visibility - Update visibility
- POST /branches/{id}/vote - Vote for branch
- DELETE /branches/{id}/vote - Remove vote
- POST /branches/{id}/link-request - Create link request
- PATCH /link-requests/{id} - Review link request
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker

from apps.novels.models import (
    Novel,
    Branch,
    BranchType,
    BranchVisibility,
    BranchVote,
    BranchLinkRequest,
    LinkRequestStatus,
)


def get_tokens_for_user(user):
    """Generate JWT tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client):
    user = baker.make("users.User")
    token = get_tokens_for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    api_client.user = user
    return api_client


@pytest.mark.django_db
class TestBranchList:
    """Tests for GET /novels/{id}/branches"""

    def test_list_branches(self, api_client):
        """Should return branches for a novel."""
        novel = baker.make(Novel)
        branch1 = baker.make(Branch, novel=novel, visibility=BranchVisibility.PUBLIC)
        branch2 = baker.make(Branch, novel=novel, visibility=BranchVisibility.LINKED)

        url = reverse("novel-branches-list", kwargs={"novel_pk": novel.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert len(response.data["data"]["results"]) == 2

    def test_list_branches_filter_by_visibility(self, api_client):
        """Should filter branches by visibility."""
        novel = baker.make(Novel)
        baker.make(Branch, novel=novel, visibility=BranchVisibility.PUBLIC)
        linked = baker.make(Branch, novel=novel, visibility=BranchVisibility.LINKED)

        url = reverse("novel-branches-list", kwargs={"novel_pk": novel.id})
        response = api_client.get(url, {"visibility": "LINKED"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]["results"]) == 1
        assert response.data["data"]["results"][0]["id"] == linked.id


@pytest.mark.django_db
class TestGetMainBranch:
    """Tests for GET /novels/{id}/branches/main"""

    def test_get_main_branch(self, api_client):
        """Should return the main branch."""
        novel = baker.make(Novel)
        main = baker.make(Branch, novel=novel, is_main=True, name="메인 브랜치")
        baker.make(Branch, novel=novel, is_main=False)

        url = reverse("novel-branches-main", kwargs={"novel_pk": novel.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["id"] == main.id
        assert response.data["data"]["is_main"] is True


@pytest.mark.django_db
class TestBranchRetrieve:
    """Tests for GET /branches/{id}"""

    def test_retrieve_branch(self, api_client):
        """Should return branch details."""
        branch = baker.make(Branch, name="테스트 브랜치")

        url = reverse("branch-detail", kwargs={"pk": branch.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["id"] == branch.id
        assert response.data["data"]["name"] == "테스트 브랜치"

    def test_retrieve_nonexistent_branch(self, api_client):
        """Should return 404 for nonexistent branch."""
        url = reverse("branch-detail", kwargs={"pk": 99999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestBranchFork:
    """Tests for POST /novels/{id}/branches"""

    def test_fork_branch_success(self, authenticated_client):
        """Should create a forked branch."""
        novel = baker.make(Novel, allow_branching=True)
        parent = baker.make(Branch, novel=novel, is_main=True)

        url = reverse("novel-branches-list", kwargs={"novel_pk": novel.id})
        data = {
            "name": "IF: 다른 선택",
            "description": "다른 선택을 했다면...",
            "branch_type": BranchType.IF_STORY,
            "fork_point_chapter": 10,
            "parent_branch_id": parent.id,
        }
        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["name"] == "IF: 다른 선택"
        assert response.data["data"]["is_main"] is False

    def test_fork_branch_not_allowed(self, authenticated_client):
        """Should fail if novel doesn't allow branching."""
        novel = baker.make(Novel, allow_branching=False)
        parent = baker.make(Branch, novel=novel, is_main=True)

        url = reverse("novel-branches-list", kwargs={"novel_pk": novel.id})
        data = {"name": "테스트", "parent_branch_id": parent.id}
        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_fork_branch_unauthenticated(self, api_client):
        """Should fail for unauthenticated user."""
        novel = baker.make(Novel)
        parent = baker.make(Branch, novel=novel, is_main=True)

        url = reverse("novel-branches-list", kwargs={"novel_pk": novel.id})
        data = {"name": "테스트", "parent_branch_id": parent.id}
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestBranchVisibilityUpdate:
    """Tests for PATCH /branches/{id}/visibility"""

    def test_update_visibility_success(self, authenticated_client):
        """Should update branch visibility."""
        branch = baker.make(
            Branch,
            author=authenticated_client.user,
            visibility=BranchVisibility.PRIVATE,
            is_main=False,
        )

        url = reverse("branch-visibility", kwargs={"pk": branch.id})
        data = {"visibility": BranchVisibility.PUBLIC}
        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["visibility"] == BranchVisibility.PUBLIC

    def test_update_visibility_not_owner(self, authenticated_client):
        """Should fail if not the owner."""
        other_user = baker.make("users.User")
        branch = baker.make(Branch, author=other_user, visibility=BranchVisibility.PRIVATE)

        url = reverse("branch-visibility", kwargs={"pk": branch.id})
        data = {"visibility": BranchVisibility.PUBLIC}
        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBranchVote:
    """Tests for POST/DELETE /branches/{id}/vote"""

    def test_vote_success(self, authenticated_client):
        """Should add vote to branch."""
        branch = baker.make(Branch, vote_count=0)

        url = reverse("branch-vote", kwargs={"pk": branch.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        branch.refresh_from_db()
        assert branch.vote_count == 1

    def test_vote_duplicate(self, authenticated_client):
        """Should fail for duplicate vote."""
        branch = baker.make(Branch, vote_count=1)
        baker.make(BranchVote, user=authenticated_client.user, branch=branch)

        url = reverse("branch-vote", kwargs={"pk": branch.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unvote_success(self, authenticated_client):
        """Should remove vote from branch."""
        branch = baker.make(Branch, vote_count=1)
        baker.make(BranchVote, user=authenticated_client.user, branch=branch)

        url = reverse("branch-vote", kwargs={"pk": branch.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        branch.refresh_from_db()
        assert branch.vote_count == 0


@pytest.mark.django_db
class TestBranchLinkRequest:
    """Tests for POST /branches/{id}/link-request"""

    def test_create_link_request_success(self, authenticated_client):
        """Should create a link request."""
        branch = baker.make(
            Branch,
            author=authenticated_client.user,
            is_main=False,
            visibility=BranchVisibility.PUBLIC,
        )

        url = reverse("branch-link-request", kwargs={"pk": branch.id})
        data = {"request_message": "연결 요청합니다."}
        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["status"] == LinkRequestStatus.PENDING

    def test_create_link_request_not_owner(self, authenticated_client):
        """Should fail if not branch owner."""
        other_user = baker.make("users.User")
        branch = baker.make(Branch, author=other_user, is_main=False)

        url = reverse("branch-link-request", kwargs={"pk": branch.id})
        data = {"request_message": "연결 요청"}
        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestLinkRequestReview:
    """Tests for PATCH /link-requests/{id}"""

    def test_approve_link_request(self, authenticated_client):
        """Should approve link request (novel author)."""
        novel = baker.make(Novel, author=authenticated_client.user)
        branch = baker.make(Branch, novel=novel, is_main=False, visibility=BranchVisibility.PUBLIC)
        link_request = baker.make(
            BranchLinkRequest, branch=branch, status=LinkRequestStatus.PENDING
        )

        url = reverse("link-request-detail", kwargs={"pk": link_request.id})
        data = {"status": LinkRequestStatus.APPROVED, "review_comment": "승인!"}
        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["status"] == LinkRequestStatus.APPROVED

        branch.refresh_from_db()
        assert branch.visibility == BranchVisibility.LINKED

    def test_reject_link_request(self, authenticated_client):
        """Should reject link request."""
        novel = baker.make(Novel, author=authenticated_client.user)
        branch = baker.make(Branch, novel=novel, is_main=False)
        link_request = baker.make(
            BranchLinkRequest, branch=branch, status=LinkRequestStatus.PENDING
        )

        url = reverse("link-request-detail", kwargs={"pk": link_request.id})
        data = {"status": LinkRequestStatus.REJECTED, "review_comment": "거절"}
        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["status"] == LinkRequestStatus.REJECTED
