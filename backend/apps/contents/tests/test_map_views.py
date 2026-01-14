"""
TDD: MapViewSet 테스트
RED → GREEN → REFACTOR
"""

import json
from typing import Any

import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.contents.models import Map, MapObject

pytestmark = pytest.mark.django_db


def get_json(response: Response) -> Any:
    """Helper to parse JSON from response content (rendered by StandardJSONRenderer)."""
    return json.loads(response.content)


class TestMapViewSet:
    """MapViewSet 테스트"""

    def setup_method(self):
        self.client = APIClient()
        self.user = baker.make("users.User")
        self.novel = baker.make("novels.Novel", author=self.user)
        self.branch = baker.make("novels.Branch", novel=self.novel, author=self.user, is_main=True)
        self.client.force_authenticate(user=self.user)

    def test_list_maps(self):
        """지도 목록 조회"""
        baker.make("contents.Map", branch=self.branch, name="지도1")
        baker.make("contents.Map", branch=self.branch, name="지도2")

        url = f"/api/v1/branches/{self.branch.id}/maps/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Paginated response
        json_data = get_json(response)
        data = json_data.get("data", {})
        results = data.get("results") or data
        assert len(results) == 2

    def test_create_map(self):
        """지도 생성"""
        url = f"/api/v1/branches/{self.branch.id}/maps/"
        data = {
            "name": "세계 지도",
            "description": "판타지 세계의 전체 지도",
            "width": 1920,
            "height": 1080,
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert get_json(response)["data"]["name"] == "세계 지도"
        assert get_json(response)["data"]["width"] == 1920

    def test_create_map_unauthenticated(self):
        """비인증 사용자 지도 생성 불가"""
        self.client.force_authenticate(user=None)
        url = f"/api/v1/branches/{self.branch.id}/maps/"
        data = {"name": "지도", "width": 800, "height": 600}

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_map(self):
        """지도 상세 조회"""
        map_obj = baker.make("contents.Map", branch=self.branch, name="테스트 지도")

        url = f"/api/v1/maps/{map_obj.id}/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert get_json(response)["data"]["name"] == "테스트 지도"

    def test_retrieve_map_with_context(self):
        """문맥 인식 지도 조회"""
        map_obj = baker.make("contents.Map", branch=self.branch, name="지도")
        baker.make("contents.MapSnapshot", map=map_obj, valid_from_chapter=1)
        baker.make("contents.MapSnapshot", map=map_obj, valid_from_chapter=5)

        url = f"/api/v1/maps/{map_obj.id}/?currentChapter=3"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        snapshot = get_json(response)["data"]["snapshot"]
        valid_from = snapshot.get("validFromChapter") or snapshot.get("valid_from_chapter")
        assert valid_from == 1

    def test_update_map(self):
        """지도 수정"""
        map_obj = baker.make("contents.Map", branch=self.branch, name="원래 지도")

        url = f"/api/v1/maps/{map_obj.id}/"
        data = {"name": "수정된 지도", "description": "새로운 설명"}

        response = self.client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert get_json(response)["data"]["name"] == "수정된 지도"

    def test_delete_map(self):
        """지도 삭제"""
        map_obj = baker.make("contents.Map", branch=self.branch)

        url = f"/api/v1/maps/{map_obj.id}/"
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Map.objects.filter(id=map_obj.id).exists()


class TestMapSnapshotViewSet:
    """MapSnapshot 관련 테스트"""

    def setup_method(self):
        self.client = APIClient()
        self.user = baker.make("users.User")
        self.novel = baker.make("novels.Novel", author=self.user)
        self.branch = baker.make("novels.Branch", novel=self.novel, author=self.user, is_main=True)
        self.map_obj = baker.make("contents.Map", branch=self.branch)
        self.client.force_authenticate(user=self.user)

    def test_create_snapshot(self):
        """스냅샷 생성"""
        url = f"/api/v1/maps/{self.map_obj.id}/snapshots/"
        data = {
            "validFromChapter": 1,
            "baseImageUrl": "https://example.com/map.png",
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        resp_data = get_json(response)["data"]
        valid_from = resp_data.get("validFromChapter") or resp_data.get("valid_from_chapter")
        assert valid_from == 1

    def test_list_snapshots(self):
        """스냅샷 목록 조회"""
        baker.make("contents.MapSnapshot", map=self.map_obj, valid_from_chapter=1)
        baker.make("contents.MapSnapshot", map=self.map_obj, valid_from_chapter=5)

        url = f"/api/v1/maps/{self.map_obj.id}/snapshots/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        json_data = get_json(response)
        data = json_data.get("data", [])
        # Check if data is already a list or has a "results" key
        results = data if isinstance(data, list) else data.get("results", data)
        assert len(results) == 2


class TestMapLayerViewSet:
    """MapLayer 관련 테스트"""

    def setup_method(self):
        self.client = APIClient()
        self.user = baker.make("users.User")
        self.novel = baker.make("novels.Novel", author=self.user)
        self.branch = baker.make("novels.Branch", novel=self.novel, author=self.user, is_main=True)
        self.map_obj = baker.make("contents.Map", branch=self.branch)
        self.snapshot = baker.make("contents.MapSnapshot", map=self.map_obj)
        self.client.force_authenticate(user=self.user)

    def test_create_layer(self):
        """레이어 생성"""
        url = f"/api/v1/snapshots/{self.snapshot.id}/layers/"
        data = {
            "name": "마커 레이어",
            "layerType": "MARKER",
            "zIndex": 1,
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert get_json(response)["data"]["name"] == "마커 레이어"

    def test_list_layers(self):
        """레이어 목록 조회"""
        baker.make("contents.MapLayer", snapshot=self.snapshot, name="레이어1")
        baker.make("contents.MapLayer", snapshot=self.snapshot, name="레이어2")

        url = f"/api/v1/snapshots/{self.snapshot.id}/layers/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        json_data = get_json(response)
        data = json_data.get("data", [])
        # Check if data is already a list or has a "results" key
        results = data if isinstance(data, list) else data.get("results", data)
        assert len(results) == 2


class TestMapObjectViewSet:
    """MapObject 관련 테스트"""

    def setup_method(self):
        self.client = APIClient()
        self.user = baker.make("users.User")
        self.novel = baker.make("novels.Novel", author=self.user)
        self.branch = baker.make("novels.Branch", novel=self.novel, author=self.user, is_main=True)
        self.map_obj = baker.make("contents.Map", branch=self.branch)
        self.snapshot = baker.make("contents.MapSnapshot", map=self.map_obj)
        self.layer = baker.make("contents.MapLayer", snapshot=self.snapshot)
        self.client.force_authenticate(user=self.user)

    def test_create_object(self):
        """오브젝트 생성"""
        url = f"/api/v1/layers/{self.layer.id}/objects/"
        data = {
            "objectType": "POINT",
            "coordinates": {"x": 100, "y": 200},
            "label": "수도",
            "description": "왕국의 수도",
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert get_json(response)["data"]["label"] == "수도"

    def test_list_objects(self):
        """오브젝트 목록 조회"""
        baker.make(
            "contents.MapObject", layer=self.layer, label="오브젝트1", coordinates={"x": 0, "y": 0}
        )
        baker.make(
            "contents.MapObject",
            layer=self.layer,
            label="오브젝트2",
            coordinates={"x": 100, "y": 100},
        )

        url = f"/api/v1/layers/{self.layer.id}/objects/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        json_data = get_json(response)
        data = json_data.get("data", [])
        # Check if data is already a list or has a "results" key
        results = data if isinstance(data, list) else data.get("results", data)
        assert len(results) == 2

    def test_create_object_with_wiki_link(self):
        """위키 연결된 오브젝트 생성"""
        wiki = baker.make("contents.WikiEntry", branch=self.branch)

        url = f"/api/v1/layers/{self.layer.id}/objects/"
        data = {
            "objectType": "ICON",
            "coordinates": {"x": 50, "y": 50},
            "label": "위키 마커",
            "wikiEntryId": wiki.id,
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        obj = MapObject.objects.get(id=get_json(response)["data"]["id"])
        assert obj.wiki_entry == wiki
