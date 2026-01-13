"""
TDD: WikiViewSet 테스트
RED → GREEN → REFACTOR
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker


pytestmark = pytest.mark.django_db


class TestWikiEntryViewSet:
    """WikiEntryViewSet 테스트"""

    def setup_method(self):
        self.client = APIClient()
        self.user = baker.make("users.User")
        self.novel = baker.make("novels.Novel", author=self.user)
        self.branch = baker.make("novels.Branch", novel=self.novel, author=self.user, is_main=True)
        self.client.force_authenticate(user=self.user)

    def test_list_wiki_entries(self):
        """위키 목록 조회"""
        baker.make("contents.WikiEntry", branch=self.branch, name="캐릭터1")
        baker.make("contents.WikiEntry", branch=self.branch, name="캐릭터2")

        url = f"/api/v1/branches/{self.branch.id}/wikis/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Paginated response
        assert "results" in response.data or "data" in response.data
        data = response.data.get("results") or response.data.get("data")
        assert len(data) == 2

    def test_create_wiki_entry(self):
        """위키 생성"""
        url = f"/api/v1/branches/{self.branch.id}/wikis/"
        data = {
            "name": "새 캐릭터",
            "imageUrl": "https://example.com/char.jpg",
            "firstAppearance": 1,
            "hiddenNote": "비밀 노트",
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["name"] == "새 캐릭터"
        # camelCase or snake_case depending on renderer
        image_url = response.data["data"].get("imageUrl") or response.data["data"].get("image_url")
        assert image_url == "https://example.com/char.jpg"

    def test_create_wiki_entry_with_initial_content(self):
        """초기 콘텐츠와 함께 위키 생성"""
        url = f"/api/v1/branches/{self.branch.id}/wikis/"
        data = {
            "name": "캐릭터",
            "initialContent": "## 캐릭터 설명\n초기 설명입니다.",
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        # 스냅샷이 생성되었는지 확인
        from apps.contents.models import WikiEntry

        wiki = WikiEntry.objects.get(id=response.data["data"]["id"])
        assert wiki.snapshots.count() == 1

    def test_create_wiki_unauthenticated(self):
        """비인증 사용자 위키 생성 불가"""
        self.client.force_authenticate(user=None)
        url = f"/api/v1/branches/{self.branch.id}/wikis/"
        data = {"name": "캐릭터"}

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_wiki_entry(self):
        """위키 상세 조회"""
        wiki = baker.make("contents.WikiEntry", branch=self.branch, name="캐릭터")

        url = f"/api/v1/wikis/{wiki.id}/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["name"] == "캐릭터"

    def test_retrieve_wiki_with_context(self):
        """문맥 인식 위키 조회"""
        wiki = baker.make("contents.WikiEntry", branch=self.branch, name="캐릭터")
        baker.make(
            "contents.WikiSnapshot",
            wiki_entry=wiki,
            valid_from_chapter=0,
            content="초기",
        )
        baker.make(
            "contents.WikiSnapshot",
            wiki_entry=wiki,
            valid_from_chapter=5,
            content="5화 이후",
        )

        # 회차 3 기준 조회
        url = f"/api/v1/wikis/{wiki.id}/?chapter=3"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["snapshot"]["content"] == "초기"

        # 회차 7 기준 조회
        url = f"/api/v1/wikis/{wiki.id}/?chapter=7"
        response = self.client.get(url)

        assert response.data["data"]["snapshot"]["content"] == "5화 이후"

    def test_update_wiki_entry(self):
        """위키 수정"""
        wiki = baker.make("contents.WikiEntry", branch=self.branch, name="캐릭터")

        url = f"/api/v1/wikis/{wiki.id}/"
        data = {"name": "수정된 캐릭터"}

        response = self.client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["name"] == "수정된 캐릭터"

    def test_delete_wiki_entry(self):
        """위키 삭제"""
        wiki = baker.make("contents.WikiEntry", branch=self.branch)

        url = f"/api/v1/wikis/{wiki.id}/"
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        from apps.contents.models import WikiEntry

        assert not WikiEntry.objects.filter(id=wiki.id).exists()


class TestWikiTagViewSet:
    """WikiTagDefinitionViewSet 테스트"""

    def setup_method(self):
        self.client = APIClient()
        self.user = baker.make("users.User")
        self.branch = baker.make("novels.Branch", author=self.user)
        self.client.force_authenticate(user=self.user)

    def test_list_tags(self):
        """태그 목록 조회"""
        baker.make(
            "contents.WikiTagDefinition",
            branch=self.branch,
            name="인물",
            display_order=1,
        )
        baker.make(
            "contents.WikiTagDefinition",
            branch=self.branch,
            name="장소",
            display_order=2,
        )

        url = f"/api/v1/branches/{self.branch.id}/wiki-tags/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 2

    def test_create_tag(self):
        """태그 생성"""
        url = f"/api/v1/branches/{self.branch.id}/wiki-tags/"
        data = {
            "name": "인물",
            "color": "#FF5733",
            "icon": "user",
            "description": "등장인물 태그",
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["name"] == "인물"
        assert response.data["data"]["color"] == "#FF5733"

    def test_delete_tag(self):
        """태그 삭제"""
        tag = baker.make("contents.WikiTagDefinition", branch=self.branch)

        url = f"/api/v1/wiki-tags/{tag.id}/"
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestWikiSnapshotViewSet:
    """WikiSnapshotViewSet 테스트"""

    def setup_method(self):
        self.client = APIClient()
        self.user = baker.make("users.User")
        self.branch = baker.make("novels.Branch", author=self.user)
        self.wiki = baker.make("contents.WikiEntry", branch=self.branch)
        self.client.force_authenticate(user=self.user)

    def test_list_snapshots(self):
        """스냅샷 목록 조회"""
        baker.make(
            "contents.WikiSnapshot",
            wiki_entry=self.wiki,
            valid_from_chapter=0,
            content="초기",
        )
        baker.make(
            "contents.WikiSnapshot",
            wiki_entry=self.wiki,
            valid_from_chapter=5,
            content="5화",
        )

        url = f"/api/v1/wikis/{self.wiki.id}/snapshots/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 2

    def test_create_snapshot(self):
        """스냅샷 생성"""
        url = f"/api/v1/wikis/{self.wiki.id}/snapshots/"
        data = {
            "content": "## 새로운 스냅샷\n회차 10부터 적용",
            "validFromChapter": 10,
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        # camelCase or snake_case depending on renderer
        valid_from = response.data["data"].get("validFromChapter") or response.data["data"].get(
            "valid_from_chapter"
        )
        assert valid_from == 10

    def test_update_tags(self):
        """위키 태그 업데이트"""
        tag1 = baker.make("contents.WikiTagDefinition", branch=self.branch, name="인물")
        tag2 = baker.make("contents.WikiTagDefinition", branch=self.branch, name="주인공")

        url = f"/api/v1/wikis/{self.wiki.id}/tags/"
        data = {"tagIds": [tag1.id, tag2.id]}

        response = self.client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        self.wiki.refresh_from_db()
        assert self.wiki.tags.count() == 2
