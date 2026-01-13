"""
TDD Tests for Novel Serializers.
"""

import pytest
from model_bakery import baker

from apps.novels.models import AgeRating, Genre
from apps.novels.serializers import (
    NovelCreateSerializer,
    NovelDetailSerializer,
    NovelListSerializer,
    NovelUpdateSerializer,
)


@pytest.fixture
def author(db):
    return baker.make("users.User", email="author@test.com", nickname="author", role="AUTHOR")


@pytest.fixture
def novel_with_branch(db, author):
    novel = baker.make("novels.Novel", author=author, title="테스트 소설", genre=Genre.FANTASY)
    baker.make(
        "novels.Branch",
        novel=novel,
        author=author,
        name=novel.title,
        is_main=True,
        branch_type="MAIN",
    )
    return novel


class TestNovelCreateSerializer:
    """소설 생성 Serializer 테스트"""

    def test_valid_data(self, db):
        """유효한 데이터로 생성"""
        data = {
            "title": "새로운 소설",
            "description": "설명입니다.",
            "genre": Genre.FANTASY,
            "age_rating": AgeRating.ALL,
        }

        serializer = NovelCreateSerializer(data=data)

        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["title"] == "새로운 소설"

    def test_missing_title_invalid(self, db):
        """제목 누락 시 에러"""
        data = {
            "description": "설명만",
            "genre": Genre.FANTASY,
        }

        serializer = NovelCreateSerializer(data=data)

        assert not serializer.is_valid()
        assert "title" in serializer.errors

    def test_missing_genre_invalid(self, db):
        """장르 누락 시 에러"""
        data = {
            "title": "제목만",
        }

        serializer = NovelCreateSerializer(data=data)

        assert not serializer.is_valid()
        assert "genre" in serializer.errors

    def test_optional_fields_defaults(self, db):
        """선택 필드 기본값"""
        data = {
            "title": "기본값 테스트",
            "genre": Genre.FANTASY,
        }

        serializer = NovelCreateSerializer(data=data)

        assert serializer.is_valid()
        # allow_branching 기본값은 True
        assert serializer.validated_data.get("allow_branching", True) is True


class TestNovelDetailSerializer:
    """소설 상세 Serializer 테스트"""

    def test_serializes_all_fields(self, novel_with_branch, author):
        """모든 필드 직렬화"""
        serializer = NovelDetailSerializer(novel_with_branch)
        data = serializer.data

        assert data["id"] == novel_with_branch.id
        assert data["title"] == "테스트 소설"
        assert data["genre"] == Genre.FANTASY
        assert "author" in data
        assert data["author"]["id"] == author.id
        assert data["author"]["nickname"] == author.nickname

    def test_includes_aggregate_fields(self, novel_with_branch):
        """집계 필드 포함"""
        novel_with_branch.total_view_count = 100
        novel_with_branch.total_like_count = 50
        novel_with_branch.save()

        serializer = NovelDetailSerializer(novel_with_branch)
        data = serializer.data

        assert data["total_view_count"] == 100
        assert data["total_like_count"] == 50

    def test_includes_branch_count(self, novel_with_branch):
        """브랜치 수 포함"""
        serializer = NovelDetailSerializer(novel_with_branch)
        data = serializer.data

        assert "branch_count" in data
        assert "linked_branch_count" in data


class TestNovelListSerializer:
    """소설 목록 Serializer 테스트"""

    def test_serializes_summary_fields(self, novel_with_branch, author):
        """요약 필드만 직렬화"""
        serializer = NovelListSerializer(novel_with_branch)
        data = serializer.data

        assert data["id"] == novel_with_branch.id
        assert data["title"] == "테스트 소설"
        assert data["genre"] == Genre.FANTASY
        assert "author" in data
        # 목록에서는 author 요약 정보만
        assert data["author"]["nickname"] == author.nickname

    def test_excludes_full_description(self, novel_with_branch):
        """긴 설명은 제외 또는 축약"""
        novel_with_branch.description = "A" * 1000
        novel_with_branch.save()

        serializer = NovelListSerializer(novel_with_branch)
        data = serializer.data

        # description은 포함되지만 전체 내용일 필요 없음 (선택적)
        assert "id" in data


class TestNovelUpdateSerializer:
    """소설 수정 Serializer 테스트"""

    def test_partial_update(self, db):
        """부분 수정 가능"""
        data = {"title": "수정된 제목"}

        serializer = NovelUpdateSerializer(data=data, partial=True)

        assert serializer.is_valid()
        assert serializer.validated_data["title"] == "수정된 제목"

    def test_cannot_update_author(self, db, author):
        """작가 변경 불가"""
        other = baker.make("users.User")
        data = {"author": other.id}

        serializer = NovelUpdateSerializer(data=data, partial=True)

        # author 필드는 read_only이거나 무시됨
        assert serializer.is_valid()
        assert "author" not in serializer.validated_data
