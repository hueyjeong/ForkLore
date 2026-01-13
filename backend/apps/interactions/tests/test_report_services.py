"""
Tests for ReportService.

TDD RED Phase: Tests written before implementation.
"""

from typing import Any

import pytest
from django.contrib.contenttypes.models import ContentType
from model_bakery import baker

from apps.contents.models import Chapter
from apps.interactions.models import Comment, Report, ReportReason, ReportStatus
from apps.interactions.services import ReportService
from apps.users.models import User


@pytest.fixture
def user(db: Any) -> User:
    """Create a regular user."""
    return baker.make("users.User")


@pytest.fixture
def admin_user(db: Any) -> User:
    """Create an admin user."""
    return baker.make("users.User", is_staff=True)


@pytest.fixture
def chapter(db: Any) -> Chapter:
    """Create a chapter for testing."""
    return baker.make("contents.Chapter")


@pytest.fixture
def comment(db: Any, user: User, chapter: Chapter) -> Comment:
    """Create a comment for testing."""
    return baker.make("interactions.Comment", user=user, chapter=chapter)


@pytest.fixture
def report_service() -> ReportService:
    """Create ReportService instance."""
    return ReportService()


class TestReportServiceCreate:
    """Tests for ReportService.create_report method."""

    def test_create_report_for_comment(
        self, report_service: ReportService, user: User, comment: Comment
    ) -> None:
        """Should create a report for a comment."""
        report = report_service.create_report(
            reporter=user,
            target=comment,
            reason=ReportReason.ABUSE,
            description="This is offensive content",
        )

        assert report.id is not None
        assert report.reporter == user
        assert report.reason == ReportReason.ABUSE
        assert report.description == "This is offensive content"
        assert report.status == ReportStatus.PENDING
        assert report.resolver is None
        assert report.resolved_at is None

        # Verify GenericFK
        content_type = ContentType.objects.get_for_model(Comment)
        assert report.content_type == content_type
        assert report.object_id == comment.id

    def test_create_report_for_chapter(
        self, report_service: ReportService, user: User, chapter: Chapter
    ) -> None:
        """Should create a report for a chapter."""
        report = report_service.create_report(
            reporter=user,
            target=chapter,
            reason=ReportReason.COPYRIGHT,
            description="Copied from another work",
        )

        assert report.id is not None
        assert report.reporter == user
        assert report.reason == ReportReason.COPYRIGHT
        assert report.status == ReportStatus.PENDING

    def test_create_report_without_description(
        self, report_service: ReportService, user: User, comment: Comment
    ) -> None:
        """Should create a report without description."""
        report = report_service.create_report(
            reporter=user,
            target=comment,
            reason=ReportReason.SPAM,
        )

        assert report.id is not None
        assert report.description == ""

    def test_create_report_duplicate_prevention(
        self, report_service: ReportService, user: User, comment: Comment
    ) -> None:
        """Should prevent duplicate reports from same user for same target."""
        # First report succeeds
        report_service.create_report(
            reporter=user,
            target=comment,
            reason=ReportReason.SPAM,
        )

        # Second report should raise error
        with pytest.raises(ValueError, match="이미 신고한 대상입니다"):
            report_service.create_report(
                reporter=user,
                target=comment,
                reason=ReportReason.ABUSE,  # Different reason, same target
            )

    def test_different_users_can_report_same_target(
        self, report_service: ReportService, comment: Comment, db: Any
    ) -> None:
        """Different users should be able to report the same target."""
        user1 = baker.make("users.User")
        user2 = baker.make("users.User")

        report1 = report_service.create_report(
            reporter=user1,
            target=comment,
            reason=ReportReason.SPAM,
        )

        report2 = report_service.create_report(
            reporter=user2,
            target=comment,
            reason=ReportReason.SPAM,
        )

        assert report1.id != report2.id
        assert Report.objects.filter(object_id=comment.id).count() == 2

    def test_user_can_report_different_targets(
        self, report_service: ReportService, user: User, chapter: Chapter, db: Any
    ) -> None:
        """Same user should be able to report different targets."""
        comment1 = baker.make("interactions.Comment", chapter=chapter)
        comment2 = baker.make("interactions.Comment", chapter=chapter)

        report1 = report_service.create_report(
            reporter=user,
            target=comment1,
            reason=ReportReason.SPAM,
        )

        report2 = report_service.create_report(
            reporter=user,
            target=comment2,
            reason=ReportReason.SPAM,
        )

        assert report1.id != report2.id


class TestReportServiceAdminResolve:
    """Tests for ReportService.admin_resolve method."""

    def test_admin_resolve_report(
        self, report_service: ReportService, admin_user: User, user: User, comment: Comment, db: Any
    ) -> None:
        """Admin should be able to resolve a report."""
        report = report_service.create_report(
            reporter=user,
            target=comment,
            reason=ReportReason.ABUSE,
        )

        resolved_report = report_service.admin_resolve(
            report_id=report.id,
            resolver=admin_user,
            note="Content removed",
        )

        assert resolved_report.status == ReportStatus.RESOLVED
        assert resolved_report.resolver == admin_user
        assert resolved_report.resolution_note == "Content removed"
        assert resolved_report.resolved_at is not None

    def test_admin_resolve_without_note(
        self, report_service: ReportService, admin_user: User, user: User, comment: Comment, db: Any
    ) -> None:
        """Admin should be able to resolve without a note."""
        report = report_service.create_report(
            reporter=user,
            target=comment,
            reason=ReportReason.SPAM,
        )

        resolved_report = report_service.admin_resolve(
            report_id=report.id,
            resolver=admin_user,
        )

        assert resolved_report.status == ReportStatus.RESOLVED
        assert resolved_report.resolution_note == ""

    def test_non_admin_cannot_resolve(
        self, report_service: ReportService, user: User, comment: Comment, db: Any
    ) -> None:
        """Non-admin users should not be able to resolve reports."""
        report = report_service.create_report(
            reporter=user,
            target=comment,
            reason=ReportReason.SPAM,
        )

        non_admin = baker.make("users.User", is_staff=False)

        with pytest.raises(PermissionError, match="관리자만 신고를 처리할 수 있습니다"):
            report_service.admin_resolve(
                report_id=report.id,
                resolver=non_admin,
            )

    def test_cannot_resolve_already_resolved(
        self, report_service: ReportService, admin_user: User, user: User, comment: Comment, db: Any
    ) -> None:
        """Should not be able to resolve an already resolved report."""
        report = report_service.create_report(
            reporter=user,
            target=comment,
            reason=ReportReason.SPAM,
        )

        # First resolution
        report_service.admin_resolve(report_id=report.id, resolver=admin_user)

        # Second resolution should fail
        with pytest.raises(ValueError, match="이미 처리된 신고입니다"):
            report_service.admin_resolve(report_id=report.id, resolver=admin_user)


class TestReportServiceAdminReject:
    """Tests for ReportService.admin_reject method."""

    def test_admin_reject_report(
        self, report_service: ReportService, admin_user: User, user: User, comment: Comment, db: Any
    ) -> None:
        """Admin should be able to reject a report."""
        report = report_service.create_report(
            reporter=user,
            target=comment,
            reason=ReportReason.ABUSE,
        )

        rejected_report = report_service.admin_reject(
            report_id=report.id,
            resolver=admin_user,
            note="No violation found",
        )

        assert rejected_report.status == ReportStatus.REJECTED
        assert rejected_report.resolver == admin_user
        assert rejected_report.resolution_note == "No violation found"
        assert rejected_report.resolved_at is not None

    def test_non_admin_cannot_reject(
        self, report_service: ReportService, user: User, comment: Comment, db: Any
    ) -> None:
        """Non-admin users should not be able to reject reports."""
        report = report_service.create_report(
            reporter=user,
            target=comment,
            reason=ReportReason.SPAM,
        )

        non_admin = baker.make("users.User", is_staff=False)

        with pytest.raises(PermissionError, match="관리자만 신고를 처리할 수 있습니다"):
            report_service.admin_reject(
                report_id=report.id,
                resolver=non_admin,
            )

    def test_cannot_reject_already_rejected(
        self, report_service: ReportService, admin_user: User, user: User, comment: Comment, db: Any
    ) -> None:
        """Should not be able to reject an already rejected report."""
        report = report_service.create_report(
            reporter=user,
            target=comment,
            reason=ReportReason.SPAM,
        )

        # First rejection
        report_service.admin_reject(report_id=report.id, resolver=admin_user)

        # Second rejection should fail
        with pytest.raises(ValueError, match="이미 처리된 신고입니다"):
            report_service.admin_reject(report_id=report.id, resolver=admin_user)


class TestReportServiceListPending:
    """Tests for ReportService.list_pending method."""

    def test_list_pending_reports(
        self, report_service: ReportService, admin_user: User, user: User, chapter: Chapter, db: Any
    ) -> None:
        """Should list all pending reports."""
        comment1 = baker.make("interactions.Comment", chapter=chapter)
        comment2 = baker.make("interactions.Comment", chapter=chapter)

        report1 = report_service.create_report(
            reporter=user,
            target=comment1,
            reason=ReportReason.SPAM,
        )
        report2 = report_service.create_report(
            reporter=user,
            target=comment2,
            reason=ReportReason.ABUSE,
        )

        # Resolve one report
        report_service.admin_resolve(report_id=report1.id, resolver=admin_user)

        pending = report_service.list_pending()

        assert len(pending) == 1
        assert pending[0].id == report2.id

    def test_list_pending_empty(self, report_service: ReportService, db: Any) -> None:
        """Should return empty list when no pending reports."""
        pending = report_service.list_pending()
        assert len(pending) == 0

    def test_list_pending_excludes_rejected(
        self, report_service: ReportService, admin_user: User, user: User, comment: Comment, db: Any
    ) -> None:
        """Should exclude rejected reports from pending list."""
        report = report_service.create_report(
            reporter=user,
            target=comment,
            reason=ReportReason.SPAM,
        )

        report_service.admin_reject(report_id=report.id, resolver=admin_user)

        pending = report_service.list_pending()
        assert len(pending) == 0


class TestReportServiceListAll:
    """Tests for ReportService.list_all method (admin)."""

    def test_list_all_reports(
        self, report_service: ReportService, admin_user: User, user: User, chapter: Chapter, db: Any
    ) -> None:
        """Should list all reports regardless of status."""
        comment1 = baker.make("interactions.Comment", chapter=chapter)
        comment2 = baker.make("interactions.Comment", chapter=chapter)
        comment3 = baker.make("interactions.Comment", chapter=chapter)

        report1 = report_service.create_report(
            reporter=user, target=comment1, reason=ReportReason.SPAM
        )
        report2 = report_service.create_report(
            reporter=user, target=comment2, reason=ReportReason.ABUSE
        )
        report_service.create_report(reporter=user, target=comment3, reason=ReportReason.SPOILER)

        # Resolve one, reject one
        report_service.admin_resolve(report_id=report1.id, resolver=admin_user)
        report_service.admin_reject(report_id=report2.id, resolver=admin_user)

        all_reports = report_service.list_all()

        assert len(all_reports) == 3

    def test_list_all_filter_by_status(
        self, report_service: ReportService, admin_user: User, user: User, chapter: Chapter, db: Any
    ) -> None:
        """Should filter reports by status."""
        comment1 = baker.make("interactions.Comment", chapter=chapter)
        comment2 = baker.make("interactions.Comment", chapter=chapter)

        report1 = report_service.create_report(
            reporter=user, target=comment1, reason=ReportReason.SPAM
        )
        report_service.create_report(reporter=user, target=comment2, reason=ReportReason.ABUSE)

        report_service.admin_resolve(report_id=report1.id, resolver=admin_user)

        resolved = report_service.list_all(status=ReportStatus.RESOLVED)
        pending = report_service.list_all(status=ReportStatus.PENDING)

        assert len(resolved) == 1
        assert len(pending) == 1
