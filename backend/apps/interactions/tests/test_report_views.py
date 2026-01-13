"""
Tests for Report API endpoints.

TDD RED Phase: Tests written before implementation.

Tests:
- POST /reports/ - Create a report (authenticated user)
- GET /admin/reports/ - List all reports (admin only)
- PATCH /admin/reports/{id}/ - Resolve/Reject report (admin only)
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker

from apps.interactions.models import ReportReason, ReportStatus, Report
from apps.users.models import User


def get_tokens_for_user(user):
    """Generate JWT tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


@pytest.fixture
def user(db):
    """Create a regular user."""
    return baker.make(User)


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return baker.make(User, is_staff=True)


@pytest.fixture
def auth_client(user):
    """Create authenticated client for regular user."""
    client = APIClient()
    tokens = get_tokens_for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    return client


@pytest.fixture
def admin_client(admin_user):
    """Create authenticated client for admin user."""
    client = APIClient()
    tokens = get_tokens_for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    return client


@pytest.fixture
def chapter(db):
    """Create a chapter."""
    return baker.make("contents.Chapter")


@pytest.fixture
def comment(db, chapter):
    """Create a comment."""
    return baker.make("interactions.Comment", chapter=chapter)


class TestReportCreate:
    """Tests for POST /reports/"""

    def test_create_report_for_comment(self, auth_client, comment):
        """Should create a report for a comment."""
        url = "/api/v1/reports/"
        data = {
            "targetType": "comment",
            "targetId": comment.id,
            "reason": "ABUSE",
            "description": "This is offensive content",
        }
        response = auth_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert resp_data["success"] is True
        assert resp_data["data"]["reason"] == "ABUSE"
        assert resp_data["data"]["status"] == "PENDING"

    def test_create_report_for_chapter(self, auth_client, chapter):
        """Should create a report for a chapter."""
        url = "/api/v1/reports/"
        data = {
            "targetType": "chapter",
            "targetId": chapter.id,
            "reason": "COPYRIGHT",
            "description": "Copied from another work",
        }
        response = auth_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_report_without_description(self, auth_client, comment):
        """Should create a report without description."""
        url = "/api/v1/reports/"
        data = {
            "targetType": "comment",
            "targetId": comment.id,
            "reason": "SPAM",
        }
        response = auth_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_report_duplicate_fails(self, auth_client, user, comment):
        """Should prevent duplicate reports from same user."""
        # Create first report directly
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(comment)
        Report.objects.create(
            reporter=user,
            content_type=content_type,
            object_id=comment.id,
            reason=ReportReason.SPAM,
            status=ReportStatus.PENDING,
        )

        # Try to create duplicate via API
        url = "/api/v1/reports/"
        data = {
            "targetType": "comment",
            "targetId": comment.id,
            "reason": "ABUSE",
        }
        response = auth_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_report_unauthenticated_fails(self, comment):
        """Should reject unauthenticated requests."""
        client = APIClient()
        url = "/api/v1/reports/"
        data = {
            "targetType": "comment",
            "targetId": comment.id,
            "reason": "SPAM",
        }
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_report_invalid_target_type_fails(self, auth_client):
        """Should reject invalid target type."""
        url = "/api/v1/reports/"
        data = {
            "targetType": "invalid_type",
            "targetId": 1,
            "reason": "SPAM",
        }
        response = auth_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_report_nonexistent_target_fails(self, auth_client):
        """Should reject non-existent target."""
        url = "/api/v1/reports/"
        data = {
            "targetType": "comment",
            "targetId": 99999,
            "reason": "SPAM",
        }
        response = auth_client.post(url, data, format="json")

        # Validation error returns 400 (target not found during serializer validation)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAdminReportList:
    """Tests for GET /admin/reports/"""

    def test_admin_list_reports(self, admin_client, admin_user, user, comment, db):
        """Admin should see all reports."""
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(comment)
        Report.objects.create(
            reporter=user,
            content_type=content_type,
            object_id=comment.id,
            reason=ReportReason.SPAM,
            status=ReportStatus.PENDING,
        )

        url = "/api/v1/admin/reports/"
        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["success"] is True
        assert len(resp_data["data"]["results"]) == 1

    def test_admin_list_filter_by_status(self, admin_client, admin_user, user, chapter, db):
        """Admin should filter reports by status."""
        from django.contrib.contenttypes.models import ContentType

        comment1 = baker.make("interactions.Comment", chapter=chapter)
        comment2 = baker.make("interactions.Comment", chapter=chapter)
        content_type = ContentType.objects.get_for_model(comment1)

        Report.objects.create(
            reporter=user,
            content_type=content_type,
            object_id=comment1.id,
            reason=ReportReason.SPAM,
            status=ReportStatus.PENDING,
        )
        Report.objects.create(
            reporter=user,
            content_type=content_type,
            object_id=comment2.id,
            reason=ReportReason.ABUSE,
            status=ReportStatus.RESOLVED,
            resolver=admin_user,
        )

        # Filter pending
        url = "/api/v1/admin/reports/?status=PENDING"
        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert len(resp_data["data"]["results"]) == 1
        assert resp_data["data"]["results"][0]["status"] == "PENDING"

    def test_non_admin_cannot_list_reports(self, auth_client):
        """Non-admin users should be forbidden."""
        url = "/api/v1/admin/reports/"
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAdminReportResolve:
    """Tests for PATCH /admin/reports/{id}/"""

    def test_admin_resolve_report(self, admin_client, admin_user, user, comment, db):
        """Admin should resolve a report."""
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(comment)
        report = Report.objects.create(
            reporter=user,
            content_type=content_type,
            object_id=comment.id,
            reason=ReportReason.SPAM,
            status=ReportStatus.PENDING,
        )

        url = f"/api/v1/admin/reports/{report.id}/"
        data = {
            "action": "resolve",
            "resolutionNote": "Content has been removed",
        }
        response = admin_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["data"]["status"] == "RESOLVED"
        assert resp_data["data"]["resolutionNote"] == "Content has been removed"

    def test_admin_reject_report(self, admin_client, admin_user, user, comment, db):
        """Admin should reject a report."""
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(comment)
        report = Report.objects.create(
            reporter=user,
            content_type=content_type,
            object_id=comment.id,
            reason=ReportReason.SPAM,
            status=ReportStatus.PENDING,
        )

        url = f"/api/v1/admin/reports/{report.id}/"
        data = {
            "action": "reject",
            "resolutionNote": "No violation found",
        }
        response = admin_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["data"]["status"] == "REJECTED"

    def test_non_admin_cannot_resolve_report(self, auth_client, user, comment, db):
        """Non-admin users should be forbidden."""
        from django.contrib.contenttypes.models import ContentType

        other_user = baker.make(User)
        content_type = ContentType.objects.get_for_model(comment)
        report = Report.objects.create(
            reporter=other_user,
            content_type=content_type,
            object_id=comment.id,
            reason=ReportReason.SPAM,
            status=ReportStatus.PENDING,
        )

        url = f"/api/v1/admin/reports/{report.id}/"
        data = {"action": "resolve"}
        response = auth_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_resolve_already_resolved_fails(self, admin_client, admin_user, user, comment, db):
        """Should fail if report is already resolved."""
        from django.contrib.contenttypes.models import ContentType
        from django.utils import timezone

        content_type = ContentType.objects.get_for_model(comment)
        report = Report.objects.create(
            reporter=user,
            content_type=content_type,
            object_id=comment.id,
            reason=ReportReason.SPAM,
            status=ReportStatus.RESOLVED,
            resolver=admin_user,
            resolved_at=timezone.now(),
        )

        url = f"/api/v1/admin/reports/{report.id}/"
        data = {"action": "resolve"}
        response = admin_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_resolve_nonexistent_report_fails(self, admin_client):
        """Should return 404 for non-existent report."""
        url = "/api/v1/admin/reports/99999/"
        data = {"action": "resolve"}
        response = admin_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_action_fails(self, admin_client, admin_user, user, comment, db):
        """Should fail with invalid action."""
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(comment)
        report = Report.objects.create(
            reporter=user,
            content_type=content_type,
            object_id=comment.id,
            reason=ReportReason.SPAM,
            status=ReportStatus.PENDING,
        )

        url = f"/api/v1/admin/reports/{report.id}/"
        data = {"action": "invalid_action"}
        response = admin_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
