"""
BranchSerializer Tests - TDD approach for Branch serializers.

Tests:
- BranchCreateSerializer: Validate fork input
- BranchDetailSerializer: Full branch output
- BranchListSerializer: Summary output for lists
- BranchLinkRequestSerializer: Link request input/output
"""

import pytest
from model_bakery import baker

from apps.novels.models import (
    Novel,
    Branch,
    BranchType,
    BranchVisibility,
    BranchLinkRequest,
    LinkRequestStatus,
)
from apps.novels.serializers import (
    BranchCreateSerializer,
    BranchDetailSerializer,
    BranchListSerializer,
    BranchLinkRequestCreateSerializer,
    BranchLinkRequestSerializer,
    BranchVisibilityUpdateSerializer,
)


@pytest.mark.django_db
class TestBranchCreateSerializer:
    """Tests for BranchCreateSerializer"""

    def test_valid_data(self):
        """Should accept valid fork data."""
        data = {
            "name": "IF: 다른 선택",
            "description": "만약 주인공이 다른 선택을 했다면...",
            "branch_type": BranchType.IF_STORY,
            "fork_point_chapter": 15,
        }

        serializer = BranchCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["name"] == "IF: 다른 선택"

    def test_missing_name_invalid(self):
        """Should reject data without name."""
        data = {
            "description": "설명만 있음",
            "branch_type": BranchType.FAN_FIC,
        }

        serializer = BranchCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_optional_fields_defaults(self):
        """Should accept minimal data with defaults."""
        data = {"name": "새 브랜치"}

        serializer = BranchCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
class TestBranchDetailSerializer:
    """Tests for BranchDetailSerializer"""

    def test_serializes_all_fields(self):
        """Should serialize all branch fields."""
        novel = baker.make(Novel)
        author = baker.make("users.User")
        branch = baker.make(
            Branch,
            novel=novel,
            author=author,
            name="테스트 브랜치",
            description="브랜치 설명",
            is_main=False,
            branch_type=BranchType.IF_STORY,
            visibility=BranchVisibility.PUBLIC,
            vote_count=100,
            view_count=5000,
        )

        serializer = BranchDetailSerializer(branch)
        data = serializer.data

        assert data["id"] == branch.id
        assert data["name"] == "테스트 브랜치"
        assert data["description"] == "브랜치 설명"
        assert data["branch_type"] == BranchType.IF_STORY
        assert data["visibility"] == BranchVisibility.PUBLIC
        assert data["is_main"] is False
        assert data["vote_count"] == 100
        assert data["view_count"] == 5000
        assert "author" in data
        assert "novel_id" in data

    def test_includes_parent_branch_info(self):
        """Should include parent branch info if exists."""
        parent = baker.make(Branch, name="부모 브랜치", is_main=True)
        child = baker.make(
            Branch,
            parent_branch=parent,
            fork_point_chapter=10,
            is_main=False,
        )

        serializer = BranchDetailSerializer(child)
        data = serializer.data

        assert data["parent_branch_id"] == parent.id
        assert data["fork_point_chapter"] == 10


@pytest.mark.django_db
class TestBranchListSerializer:
    """Tests for BranchListSerializer"""

    def test_serializes_summary_fields(self):
        """Should serialize only summary fields."""
        branch = baker.make(
            Branch,
            name="요약 브랜치",
            branch_type=BranchType.SIDE_STORY,
            visibility=BranchVisibility.LINKED,
            vote_count=50,
            chapter_count=10,
        )

        serializer = BranchListSerializer(branch)
        data = serializer.data

        assert data["id"] == branch.id
        assert data["name"] == "요약 브랜치"
        assert data["branch_type"] == BranchType.SIDE_STORY
        assert data["visibility"] == BranchVisibility.LINKED
        assert data["vote_count"] == 50
        assert data["chapter_count"] == 10

    def test_excludes_full_description(self):
        """Should not include full description in list."""
        branch = baker.make(
            Branch,
            description="아주 긴 브랜치 설명입니다. " * 50,
        )

        serializer = BranchListSerializer(branch)
        data = serializer.data

        # description should be truncated or not present
        # (depending on implementation)
        assert "description" not in data or len(data.get("description", "")) < 200


@pytest.mark.django_db
class TestBranchVisibilityUpdateSerializer:
    """Tests for BranchVisibilityUpdateSerializer"""

    def test_valid_visibility(self):
        """Should accept valid visibility values."""
        data = {"visibility": BranchVisibility.PUBLIC}

        serializer = BranchVisibilityUpdateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_invalid_visibility(self):
        """Should reject invalid visibility value."""
        data = {"visibility": "INVALID"}

        serializer = BranchVisibilityUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert "visibility" in serializer.errors


@pytest.mark.django_db
class TestBranchLinkRequestCreateSerializer:
    """Tests for BranchLinkRequestCreateSerializer"""

    def test_valid_data(self):
        """Should accept valid link request data."""
        data = {"request_message": "작품 페이지에 연결을 요청합니다."}

        serializer = BranchLinkRequestCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_empty_message_allowed(self):
        """Should allow empty message."""
        data = {}

        serializer = BranchLinkRequestCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
class TestBranchLinkRequestSerializer:
    """Tests for BranchLinkRequestSerializer"""

    def test_serializes_all_fields(self):
        """Should serialize all link request fields."""
        branch = baker.make(Branch)
        reviewer = baker.make("users.User")
        link_request = baker.make(
            BranchLinkRequest,
            branch=branch,
            status=LinkRequestStatus.PENDING,
            request_message="연결 요청합니다",
            reviewer=reviewer,
            review_comment="검토 코멘트",
        )

        serializer = BranchLinkRequestSerializer(link_request)
        data = serializer.data

        assert data["id"] == link_request.id
        assert data["status"] == LinkRequestStatus.PENDING
        assert data["request_message"] == "연결 요청합니다"
        assert data["review_comment"] == "검토 코멘트"
        assert "branch_id" in data
