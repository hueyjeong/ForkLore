"""
BranchLinkService Tests - TDD approach for Branch Link Request system.

Tests:
- request_link(): Create a link request
- approve_link(): Approve a link request (original author only)
- reject_link(): Reject a link request
- list_requests(): List link requests for a branch
"""

import pytest
from django.utils import timezone
from model_bakery import baker

from apps.novels.models import (
    Novel,
    Branch,
    BranchLinkRequest,
    BranchVisibility,
    LinkRequestStatus,
)
from apps.novels.services import BranchLinkService


@pytest.mark.django_db
class TestBranchLinkServiceRequestLink:
    """Tests for BranchLinkService.request_link()"""

    def test_request_link_success(self):
        """Should create a link request for a branch."""
        service = BranchLinkService()
        branch_author = baker.make("users.User")
        branch = baker.make(
            Branch,
            author=branch_author,
            is_main=False,
            visibility=BranchVisibility.PUBLIC,
        )

        result = service.request_link(
            branch_id=branch.id,
            requester=branch_author,
            message="작품 페이지에 연결을 요청합니다.",
        )

        assert result.branch == branch
        assert result.status == LinkRequestStatus.PENDING
        assert result.request_message == "작품 페이지에 연결을 요청합니다."

    def test_request_link_not_branch_author_raises_error(self):
        """Should raise error if requester is not branch author."""
        service = BranchLinkService()
        branch_author = baker.make("users.User")
        other_user = baker.make("users.User")
        branch = baker.make(Branch, author=branch_author)

        with pytest.raises(PermissionError) as exc_info:
            service.request_link(
                branch_id=branch.id,
                requester=other_user,
                message="연결 요청",
            )

        assert "브랜치 작성자만" in str(exc_info.value)

    def test_request_link_main_branch_raises_error(self):
        """Should raise error for main branch link request."""
        service = BranchLinkService()
        user = baker.make("users.User")
        branch = baker.make(Branch, author=user, is_main=True)

        with pytest.raises(ValueError) as exc_info:
            service.request_link(
                branch_id=branch.id,
                requester=user,
                message="연결 요청",
            )

        assert "메인 브랜치" in str(exc_info.value)

    def test_request_link_already_linked_raises_error(self):
        """Should raise error if branch is already LINKED."""
        service = BranchLinkService()
        user = baker.make("users.User")
        branch = baker.make(Branch, author=user, is_main=False, visibility=BranchVisibility.LINKED)

        with pytest.raises(ValueError) as exc_info:
            service.request_link(
                branch_id=branch.id,
                requester=user,
                message="연결 요청",
            )

        assert "이미 연결된" in str(exc_info.value)

    def test_request_link_pending_request_exists_raises_error(self):
        """Should raise error if pending request already exists."""
        service = BranchLinkService()
        user = baker.make("users.User")
        branch = baker.make(Branch, author=user, is_main=False, visibility=BranchVisibility.PUBLIC)
        baker.make(BranchLinkRequest, branch=branch, status=LinkRequestStatus.PENDING)

        with pytest.raises(ValueError) as exc_info:
            service.request_link(
                branch_id=branch.id,
                requester=user,
                message="또 다른 요청",
            )

        assert "대기중인 요청" in str(exc_info.value)


@pytest.mark.django_db
class TestBranchLinkServiceApproveLink:
    """Tests for BranchLinkService.approve_link()"""

    def test_approve_link_success(self):
        """Should approve link request and change branch visibility to LINKED."""
        service = BranchLinkService()
        novel_author = baker.make("users.User")
        novel = baker.make(Novel, author=novel_author, linked_branch_count=0)
        branch = baker.make(
            Branch,
            novel=novel,
            is_main=False,
            visibility=BranchVisibility.PUBLIC,
        )
        link_request = baker.make(
            BranchLinkRequest, branch=branch, status=LinkRequestStatus.PENDING
        )

        result = service.approve_link(
            request_id=link_request.id,
            reviewer=novel_author,
            comment="승인합니다!",
        )

        assert result.status == LinkRequestStatus.APPROVED
        assert result.reviewer == novel_author
        assert result.review_comment == "승인합니다!"
        assert result.reviewed_at is not None

        branch.refresh_from_db()
        assert branch.visibility == BranchVisibility.LINKED

        novel.refresh_from_db()
        assert novel.linked_branch_count == 1

    def test_approve_link_not_novel_author_raises_error(self):
        """Should raise error if reviewer is not the novel author."""
        service = BranchLinkService()
        novel_author = baker.make("users.User")
        other_user = baker.make("users.User")
        novel = baker.make(Novel, author=novel_author)
        branch = baker.make(Branch, novel=novel)
        link_request = baker.make(
            BranchLinkRequest, branch=branch, status=LinkRequestStatus.PENDING
        )

        with pytest.raises(PermissionError) as exc_info:
            service.approve_link(
                request_id=link_request.id,
                reviewer=other_user,
                comment="승인",
            )

        assert "원작 작가만" in str(exc_info.value)

    def test_approve_link_not_pending_raises_error(self):
        """Should raise error if request is not pending."""
        service = BranchLinkService()
        novel_author = baker.make("users.User")
        novel = baker.make(Novel, author=novel_author)
        branch = baker.make(Branch, novel=novel)
        link_request = baker.make(
            BranchLinkRequest, branch=branch, status=LinkRequestStatus.APPROVED
        )

        with pytest.raises(ValueError) as exc_info:
            service.approve_link(
                request_id=link_request.id,
                reviewer=novel_author,
                comment="다시 승인",
            )

        assert "대기중인 요청만" in str(exc_info.value)


@pytest.mark.django_db
class TestBranchLinkServiceRejectLink:
    """Tests for BranchLinkService.reject_link()"""

    def test_reject_link_success(self):
        """Should reject link request."""
        service = BranchLinkService()
        novel_author = baker.make("users.User")
        novel = baker.make(Novel, author=novel_author)
        branch = baker.make(Branch, novel=novel, visibility=BranchVisibility.PUBLIC)
        link_request = baker.make(
            BranchLinkRequest, branch=branch, status=LinkRequestStatus.PENDING
        )

        result = service.reject_link(
            request_id=link_request.id,
            reviewer=novel_author,
            comment="스토리가 맞지 않습니다.",
        )

        assert result.status == LinkRequestStatus.REJECTED
        assert result.reviewer == novel_author
        assert result.review_comment == "스토리가 맞지 않습니다."
        assert result.reviewed_at is not None

        branch.refresh_from_db()
        assert branch.visibility == BranchVisibility.PUBLIC  # unchanged

    def test_reject_link_not_novel_author_raises_error(self):
        """Should raise error if reviewer is not the novel author."""
        service = BranchLinkService()
        novel_author = baker.make("users.User")
        other_user = baker.make("users.User")
        novel = baker.make(Novel, author=novel_author)
        branch = baker.make(Branch, novel=novel)
        link_request = baker.make(
            BranchLinkRequest, branch=branch, status=LinkRequestStatus.PENDING
        )

        with pytest.raises(PermissionError) as exc_info:
            service.reject_link(
                request_id=link_request.id,
                reviewer=other_user,
                comment="거절",
            )

        assert "원작 작가만" in str(exc_info.value)


@pytest.mark.django_db
class TestBranchLinkServiceListRequests:
    """Tests for BranchLinkService.list_requests()"""

    def test_list_requests_for_branch(self):
        """Should list all link requests for a branch."""
        service = BranchLinkService()
        branch = baker.make(Branch)
        request1 = baker.make(BranchLinkRequest, branch=branch)
        request2 = baker.make(BranchLinkRequest, branch=branch)
        baker.make(BranchLinkRequest)  # different branch

        result = service.list_requests(branch_id=branch.id)

        assert result.count() == 2
        assert request1 in result
        assert request2 in result

    def test_list_requests_filter_by_status(self):
        """Should filter requests by status."""
        service = BranchLinkService()
        branch = baker.make(Branch)
        pending = baker.make(BranchLinkRequest, branch=branch, status=LinkRequestStatus.PENDING)
        baker.make(BranchLinkRequest, branch=branch, status=LinkRequestStatus.APPROVED)

        result = service.list_requests(branch_id=branch.id, status=LinkRequestStatus.PENDING)

        assert result.count() == 1
        assert pending in result
