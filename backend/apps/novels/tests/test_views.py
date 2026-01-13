"""
Integration tests for Novel API endpoints.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker

from apps.novels.models import Novel, Branch, Genre, AgeRating, NovelStatus


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def author(db):
    return baker.make("users.User", email="author@test.com", nickname="author", role="AUTHOR")


@pytest.fixture
def other_author(db):
    return baker.make("users.User", email="other@test.com", nickname="other", role="AUTHOR")


@pytest.fixture
def authenticated_client(api_client, author):
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(author)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def other_authenticated_client(api_client, other_author):
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(other_author)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def novel(db, author):
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


def get_json(response):
    """Helper to get JSON data from response."""
    return response.json()


class TestNovelCreate:
    """POST /api/v1/novels - 소설 생성"""

    def test_create_novel_success(self, authenticated_client, author):
        """인증된 작가가 소설 생성"""
        url = reverse("novel-list")
        data = {
            "title": "새로운 소설",
            "description": "설명입니다.",
            "genre": Genre.FANTASY,
            "ageRating": AgeRating.ALL,
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        json_data = get_json(response)
        assert json_data["success"] is True
        assert json_data["data"]["title"] == "새로운 소설"

        # 메인 브랜치 자동 생성 확인
        novel = Novel.objects.get(id=json_data["data"]["id"])
        assert novel.branches.filter(is_main=True).exists()

    def test_create_novel_unauthenticated(self, api_client):
        """미인증 사용자는 생성 불가"""
        url = reverse("novel-list")
        data = {"title": "테스트", "genre": Genre.FANTASY}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_novel_missing_required_fields(self, authenticated_client):
        """필수 필드 누락 시 400 에러"""
        url = reverse("novel-list")
        data = {"description": "설명만"}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestNovelList:
    """GET /api/v1/novels - 소설 목록"""

    def test_list_novels(self, api_client, novel):
        """소설 목록 조회 (인증 불필요)"""
        url = reverse("novel-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        json_data = get_json(response)
        assert json_data["success"] is True
        assert len(json_data["data"]["results"]) >= 1

    def test_list_novels_filter_by_genre(self, api_client, author):
        """장르 필터링"""
        baker.make("novels.Novel", author=author, genre=Genre.FANTASY)
        baker.make("novels.Novel", author=author, genre=Genre.ROMANCE)

        url = reverse("novel-list")
        response = api_client.get(url, {"genre": Genre.FANTASY})

        json_data = get_json(response)
        for novel in json_data["data"]["results"]:
            assert novel["genre"] == Genre.FANTASY

    def test_list_novels_pagination(self, api_client, author):
        """페이지네이션"""
        for i in range(25):
            baker.make("novels.Novel", author=author, title=f"소설 {i}")

        url = reverse("novel-list")
        response = api_client.get(url, {"page": 1, "size": 10})

        json_data = get_json(response)
        assert len(json_data["data"]["results"]) == 10
        assert json_data["data"]["count"] >= 25

    def test_list_novels_sort_by_popular(self, api_client, author):
        """인기순 정렬"""
        baker.make("novels.Novel", author=author, total_view_count=100)
        baker.make("novels.Novel", author=author, total_view_count=500)

        url = reverse("novel-list")
        response = api_client.get(url, {"sort": "popular"})

        json_data = get_json(response)
        results = json_data["data"]["results"]
        assert results[0]["totalViewCount"] >= results[-1]["totalViewCount"]


class TestNovelRetrieve:
    """GET /api/v1/novels/{id} - 소설 상세"""

    def test_retrieve_novel(self, api_client, novel):
        """소설 상세 조회"""
        url = reverse("novel-detail", kwargs={"pk": novel.id})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        json_data = get_json(response)
        assert json_data["success"] is True
        assert json_data["data"]["id"] == novel.id
        assert json_data["data"]["title"] == novel.title
        assert "author" in json_data["data"]

    def test_retrieve_nonexistent_novel(self, api_client, db):
        """존재하지 않는 소설 조회"""
        url = reverse("novel-detail", kwargs={"pk": 99999})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_deleted_novel(self, api_client, novel):
        """삭제된 소설 조회 시 404"""
        novel.soft_delete()
        url = reverse("novel-detail", kwargs={"pk": novel.id})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestNovelUpdate:
    """PATCH /api/v1/novels/{id} - 소설 수정"""

    def test_update_novel_success(self, authenticated_client, novel, author):
        """소설 작가가 수정"""
        url = reverse("novel-detail", kwargs={"pk": novel.id})
        data = {"title": "수정된 제목"}

        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        json_data = get_json(response)
        assert json_data["data"]["title"] == "수정된 제목"

    def test_update_novel_not_owner(self, other_authenticated_client, novel):
        """다른 작가는 수정 불가"""
        url = reverse("novel-detail", kwargs={"pk": novel.id})
        data = {"title": "해킹 시도"}

        response = other_authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_novel_unauthenticated(self, api_client, novel):
        """미인증 사용자는 수정 불가"""
        url = reverse("novel-detail", kwargs={"pk": novel.id})
        data = {"title": "해킹 시도"}

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestNovelDelete:
    """DELETE /api/v1/novels/{id} - 소설 삭제"""

    def test_delete_novel_success(self, authenticated_client, novel, author):
        """소설 작가가 삭제 (소프트)"""
        url = reverse("novel-detail", kwargs={"pk": novel.id})

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 소프트 삭제 확인
        novel.refresh_from_db()
        assert novel.is_deleted is True

    def test_delete_novel_not_owner(self, other_authenticated_client, novel):
        """다른 작가는 삭제 불가"""
        url = reverse("novel-detail", kwargs={"pk": novel.id})

        response = other_authenticated_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_novel_unauthenticated(self, api_client, novel):
        """미인증 사용자는 삭제 불가"""
        url = reverse("novel-detail", kwargs={"pk": novel.id})

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
