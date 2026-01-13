"""
TDD Tests for NovelService.

RED-GREEN-REFACTOR:
1. Write failing tests first
2. Implement minimal code to pass
3. Refactor
"""

import pytest
from model_bakery import baker

from apps.novels.models import AgeRating, Branch, BranchType, Genre, Novel, NovelStatus
from apps.novels.services import NovelService


@pytest.fixture
def novel_service():
    return NovelService()


@pytest.fixture
def author(db):
    return baker.make("users.User", email="author@test.com", nickname="author", role="AUTHOR")


@pytest.fixture
def other_author(db):
    return baker.make("users.User", email="other@test.com", nickname="other", role="AUTHOR")


class TestNovelServiceCreate:
    """소설 생성 서비스 테스트"""

    def test_create_novel_success(self, novel_service, author):
        """소설 생성 시 메인 브랜치도 자동 생성"""
        data = {
            "title": "테스트 소설",
            "description": "테스트 설명입니다.",
            "genre": Genre.FANTASY,
            "age_rating": AgeRating.ALL,
        }

        novel = novel_service.create(author=author, data=data)

        assert novel.id is not None
        assert novel.title == "테스트 소설"
        assert novel.description == "테스트 설명입니다."
        assert novel.genre == Genre.FANTASY
        assert novel.age_rating == AgeRating.ALL
        assert novel.status == NovelStatus.ONGOING
        assert novel.author == author
        assert novel.allow_branching is True

        # 메인 브랜치 자동 생성 확인
        main_branch = Branch.objects.filter(novel=novel, is_main=True).first()
        assert main_branch is not None
        assert main_branch.name == novel.title
        assert main_branch.author == author
        assert main_branch.branch_type == BranchType.MAIN
        assert main_branch.visibility == "PUBLIC"

    def test_create_novel_with_all_fields(self, novel_service, author):
        """모든 필드를 포함한 소설 생성"""
        data = {
            "title": "완전한 소설",
            "description": "완전한 설명",
            "cover_image_url": "https://example.com/cover.jpg",
            "genre": Genre.ROMANCE,
            "age_rating": AgeRating.AGE_15,
            "allow_branching": False,
        }

        novel = novel_service.create(author=author, data=data)

        assert novel.cover_image_url == "https://example.com/cover.jpg"
        assert novel.age_rating == AgeRating.AGE_15
        assert novel.allow_branching is False

    def test_create_novel_requires_title(self, novel_service, author):
        """제목 없이 소설 생성 시 에러"""
        data = {
            "description": "설명만",
            "genre": Genre.FANTASY,
        }

        with pytest.raises((ValueError, KeyError)):
            novel_service.create(author=author, data=data)


class TestNovelServiceList:
    """소설 목록 조회 서비스 테스트"""

    def test_list_novels_returns_queryset(self, novel_service, author):
        """소설 목록 조회 - 삭제되지 않은 소설만 반환"""
        novel1 = baker.make("novels.Novel", author=author, title="소설1")
        novel2 = baker.make("novels.Novel", author=author, title="소설2")
        deleted_novel = baker.make("novels.Novel", author=author, title="삭제된 소설")
        deleted_novel.soft_delete()

        novels = novel_service.list()

        assert novels.count() == 2
        assert novel1 in novels
        assert novel2 in novels
        assert deleted_novel not in novels

    def test_list_novels_filter_by_genre(self, novel_service, author):
        """장르 필터링"""
        fantasy = baker.make("novels.Novel", author=author, genre=Genre.FANTASY)
        romance = baker.make("novels.Novel", author=author, genre=Genre.ROMANCE)

        novels = novel_service.list(filters={"genre": Genre.FANTASY})

        assert novels.count() == 1
        assert fantasy in novels
        assert romance not in novels

    def test_list_novels_filter_by_status(self, novel_service, author):
        """상태 필터링"""
        ongoing = baker.make("novels.Novel", author=author, status=NovelStatus.ONGOING)
        baker.make("novels.Novel", author=author, status=NovelStatus.COMPLETED)

        novels = novel_service.list(filters={"status": NovelStatus.ONGOING})

        assert novels.count() == 1
        assert ongoing in novels

    def test_list_novels_sort_by_popular(self, novel_service, author):
        """인기순 정렬 (총 조회수 기준)"""
        novel1 = baker.make("novels.Novel", author=author, total_view_count=100)
        novel2 = baker.make("novels.Novel", author=author, total_view_count=500)
        novel3 = baker.make("novels.Novel", author=author, total_view_count=50)

        novels = novel_service.list(sort="popular")

        novels_list = list(novels)
        assert novels_list[0] == novel2
        assert novels_list[1] == novel1
        assert novels_list[2] == novel3

    def test_list_novels_sort_by_latest(self, novel_service, author):
        """최신순 정렬"""
        novels = novel_service.list(sort="latest")

        # 기본이 최신순
        assert novels.query.order_by[0] == "-created_at"


class TestNovelServiceRetrieve:
    """소설 상세 조회 서비스 테스트"""

    def test_retrieve_novel_success(self, novel_service, author):
        """소설 상세 조회"""
        novel = baker.make("novels.Novel", author=author, title="조회할 소설")

        result = novel_service.retrieve(novel_id=novel.id)

        assert result == novel
        assert result.title == "조회할 소설"

    def test_retrieve_deleted_novel_raises_error(self, novel_service, author):
        """삭제된 소설 조회 시 에러"""
        novel = baker.make("novels.Novel", author=author)
        novel.soft_delete()

        with pytest.raises(Novel.DoesNotExist):
            novel_service.retrieve(novel_id=novel.id)

    def test_retrieve_nonexistent_novel_raises_error(self, novel_service, db):
        """존재하지 않는 소설 조회 시 에러"""
        with pytest.raises(Novel.DoesNotExist):
            novel_service.retrieve(novel_id=99999)


class TestNovelServiceUpdate:
    """소설 수정 서비스 테스트"""

    def test_update_novel_success(self, novel_service, author):
        """소설 수정 성공"""
        novel = baker.make("novels.Novel", author=author, title="원본 제목")

        updated = novel_service.update(
            novel_id=novel.id,
            author=author,
            data={"title": "수정된 제목", "description": "수정된 설명"},
        )

        assert updated.title == "수정된 제목"
        assert updated.description == "수정된 설명"

    def test_update_novel_not_owner_raises_error(self, novel_service, author, other_author):
        """작가가 아닌 사용자가 수정 시 에러"""
        novel = baker.make("novels.Novel", author=author)

        with pytest.raises(PermissionError):
            novel_service.update(
                novel_id=novel.id,
                author=other_author,
                data={"title": "해킹 시도"},
            )

    def test_update_novel_partial(self, novel_service, author):
        """부분 수정 (일부 필드만)"""
        novel = baker.make(
            "novels.Novel",
            author=author,
            title="원본 제목",
            description="원본 설명",
        )

        updated = novel_service.update(
            novel_id=novel.id,
            author=author,
            data={"title": "수정된 제목만"},
        )

        assert updated.title == "수정된 제목만"
        assert updated.description == "원본 설명"  # 변경되지 않음


class TestNovelServiceDelete:
    """소설 삭제 서비스 테스트"""

    def test_delete_novel_soft_delete(self, novel_service, author):
        """소설 소프트 삭제"""
        novel = baker.make("novels.Novel", author=author)

        novel_service.delete(novel_id=novel.id, author=author)

        novel.refresh_from_db()
        assert novel.is_deleted is True
        assert novel.deleted_at is not None

    def test_delete_novel_not_owner_raises_error(self, novel_service, author, other_author):
        """작가가 아닌 사용자가 삭제 시 에러"""
        novel = baker.make("novels.Novel", author=author)

        with pytest.raises(PermissionError):
            novel_service.delete(novel_id=novel.id, author=other_author)

    def test_delete_already_deleted_raises_error(self, novel_service, author):
        """이미 삭제된 소설 삭제 시 에러"""
        novel = baker.make("novels.Novel", author=author)
        novel.soft_delete()

        with pytest.raises(Novel.DoesNotExist):
            novel_service.delete(novel_id=novel.id, author=author)
