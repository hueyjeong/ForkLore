"""
TDD: MapService 테스트
RED → GREEN → REFACTOR
"""

import pytest
from django.core.exceptions import PermissionDenied
from model_bakery import baker

from apps.contents.map_services import MapService
from apps.contents.models import LayerType, Map, ObjectType

pytestmark = pytest.mark.django_db


class TestMapServiceCreate:
    """MapService.create() 테스트"""

    def test_create_map(self):
        """지도 생성"""
        user = baker.make("users.User")
        branch = baker.make("novels.Branch", author=user)

        map_obj = MapService.create(
            branch_id=branch.id,
            user=user,
            name="세계 지도",
            description="판타지 세계의 전체 지도",
            width=1920,
            height=1080,
        )

        assert map_obj.id is not None
        assert map_obj.branch == branch
        assert map_obj.name == "세계 지도"
        assert map_obj.description == "판타지 세계의 전체 지도"
        assert map_obj.width == 1920
        assert map_obj.height == 1080

    def test_create_map_only_author(self):
        """브랜치 작가만 지도 생성 가능"""
        author = baker.make("users.User")
        other_user = baker.make("users.User")
        branch = baker.make("novels.Branch", author=author)

        with pytest.raises(PermissionDenied):
            MapService.create(
                branch_id=branch.id,
                user=other_user,
                name="지도",
                width=800,
                height=600,
            )

    def test_create_map_duplicate_name_error(self):
        """같은 브랜치에서 중복 이름 오류"""
        branch = baker.make("novels.Branch")
        user = branch.author
        MapService.create(branch_id=branch.id, user=user, name="지도A", width=800, height=600)

        with pytest.raises(ValueError) as exc_info:
            MapService.create(branch_id=branch.id, user=user, name="지도A", width=800, height=600)
        assert "이미 존재하는" in str(exc_info.value)

    def test_create_map_branch_not_found(self):
        """존재하지 않는 브랜치"""
        user = baker.make("users.User")

        with pytest.raises(ValueError) as exc_info:
            MapService.create(branch_id=99999, user=user, name="지도", width=800, height=600)
        assert "존재하지 않는 브랜치" in str(exc_info.value)


class TestMapServiceUpdate:
    """MapService.update() 테스트"""

    def test_update_map(self):
        """지도 업데이트"""
        branch = baker.make("novels.Branch")
        map_obj = baker.make("contents.Map", branch=branch, name="원래 지도", width=800, height=600)
        user = branch.author

        updated = MapService.update(
            map_id=map_obj.id,
            user=user,
            name="수정된 지도",
            description="새로운 설명",
        )

        assert updated.name == "수정된 지도"
        assert updated.description == "새로운 설명"

    def test_update_map_only_author(self):
        """브랜치 작가만 수정 가능"""
        branch = baker.make("novels.Branch")
        map_obj = baker.make("contents.Map", branch=branch)
        other_user = baker.make("users.User")

        with pytest.raises(PermissionDenied):
            MapService.update(map_id=map_obj.id, user=other_user, name="수정")


class TestMapServiceRetrieve:
    """MapService.retrieve() 테스트"""

    def test_retrieve_map(self):
        """지도 조회"""
        map_obj = baker.make("contents.Map", name="테스트 지도")

        result = MapService.retrieve(map_obj.id)

        assert result.id == map_obj.id
        assert result.name == "테스트 지도"

    def test_retrieve_map_not_found(self):
        """존재하지 않는 지도"""
        with pytest.raises(ValueError) as exc_info:
            MapService.retrieve(99999)
        assert "존재하지 않는 지도" in str(exc_info.value)


class TestMapServiceList:
    """MapService.list() 테스트"""

    def test_list_maps(self):
        """브랜치의 지도 목록"""
        branch = baker.make("novels.Branch")
        baker.make("contents.Map", branch=branch, name="지도A")
        baker.make("contents.Map", branch=branch, name="지도B")
        baker.make("contents.Map")  # 다른 브랜치

        maps = MapService.list(branch.id)

        assert maps.count() == 2

    def test_list_maps_empty(self):
        """지도 없는 브랜치"""
        branch = baker.make("novels.Branch")

        maps = MapService.list(branch.id)

        assert maps.count() == 0


class TestMapServiceDelete:
    """MapService.delete() 테스트"""

    def test_delete_map(self):
        """지도 삭제"""
        branch = baker.make("novels.Branch")
        map_obj = baker.make("contents.Map", branch=branch)
        user = branch.author

        MapService.delete(map_obj.id, user)

        assert not Map.objects.filter(id=map_obj.id).exists()

    def test_delete_map_only_author(self):
        """브랜치 작가만 삭제 가능"""
        branch = baker.make("novels.Branch")
        map_obj = baker.make("contents.Map", branch=branch)
        other_user = baker.make("users.User")

        with pytest.raises(PermissionDenied):
            MapService.delete(map_obj.id, other_user)


class TestMapServiceCreateSnapshot:
    """MapService.create_snapshot() 테스트"""

    def test_create_snapshot(self):
        """스냅샷 생성"""
        branch = baker.make("novels.Branch")
        map_obj = baker.make("contents.Map", branch=branch)
        user = branch.author

        snapshot = MapService.create_snapshot(
            map_id=map_obj.id,
            user=user,
            valid_from_chapter=1,
            base_image_url="https://example.com/map.png",
        )

        assert snapshot.id is not None
        assert snapshot.map == map_obj
        assert snapshot.valid_from_chapter == 1
        assert snapshot.base_image_url == "https://example.com/map.png"

    def test_create_snapshot_duplicate_chapter_error(self):
        """같은 회차에 중복 스냅샷 오류"""
        branch = baker.make("novels.Branch")
        map_obj = baker.make("contents.Map", branch=branch)
        user = branch.author
        MapService.create_snapshot(map_id=map_obj.id, user=user, valid_from_chapter=1)

        with pytest.raises(ValueError) as exc_info:
            MapService.create_snapshot(map_id=map_obj.id, user=user, valid_from_chapter=1)
        assert "스냅샷이 존재합니다" in str(exc_info.value)


class TestMapServiceAddLayer:
    """MapService.add_layer() 테스트"""

    def test_add_layer(self):
        """레이어 추가"""
        branch = baker.make("novels.Branch")
        map_obj = baker.make("contents.Map", branch=branch)
        snapshot = baker.make("contents.MapSnapshot", map=map_obj)
        user = branch.author

        layer = MapService.add_layer(
            snapshot_id=snapshot.id,
            user=user,
            name="마커 레이어",
            layer_type=LayerType.MARKER,
            z_index=1,
        )

        assert layer.id is not None
        assert layer.snapshot == snapshot
        assert layer.name == "마커 레이어"
        assert layer.layer_type == LayerType.MARKER
        assert layer.z_index == 1


class TestMapServiceAddObject:
    """MapService.add_object() 테스트"""

    def test_add_object(self):
        """오브젝트 추가"""
        branch = baker.make("novels.Branch")
        map_obj = baker.make("contents.Map", branch=branch)
        snapshot = baker.make("contents.MapSnapshot", map=map_obj)
        layer = baker.make("contents.MapLayer", snapshot=snapshot)
        user = branch.author

        obj = MapService.add_object(
            layer_id=layer.id,
            user=user,
            object_type=ObjectType.POINT,
            coordinates={"x": 100, "y": 200},
            label="수도",
            description="왕국의 수도",
        )

        assert obj.id is not None
        assert obj.layer == layer
        assert obj.object_type == ObjectType.POINT
        assert obj.coordinates == {"x": 100, "y": 200}
        assert obj.label == "수도"

    def test_add_object_with_wiki_link(self):
        """위키 연결된 오브젝트 추가"""
        branch = baker.make("novels.Branch")
        map_obj = baker.make("contents.Map", branch=branch)
        snapshot = baker.make("contents.MapSnapshot", map=map_obj)
        layer = baker.make("contents.MapLayer", snapshot=snapshot)
        wiki = baker.make("contents.WikiEntry", branch=branch)
        user = branch.author

        obj = MapService.add_object(
            layer_id=layer.id,
            user=user,
            object_type=ObjectType.ICON,
            coordinates={"x": 50, "y": 50},
            label="위키 마커",
            wiki_entry_id=wiki.id,
        )

        assert obj.wiki_entry == wiki


class TestMapServiceGetForChapter:
    """MapService.get_for_chapter() 테스트 - 문맥 인식 조회"""

    def test_get_for_chapter_exact_match(self):
        """정확한 회차 스냅샷 조회"""
        map_obj = baker.make("contents.Map")
        snapshot1 = baker.make("contents.MapSnapshot", map=map_obj, valid_from_chapter=1)
        baker.make("contents.MapSnapshot", map=map_obj, valid_from_chapter=5)

        result = MapService.get_for_chapter(map_obj.id, chapter_number=3)

        assert result["snapshot"].id == snapshot1.id

    def test_get_for_chapter_latest_valid(self):
        """현재 회차 이하의 가장 최신 스냅샷"""
        map_obj = baker.make("contents.Map")
        baker.make("contents.MapSnapshot", map=map_obj, valid_from_chapter=1)
        snapshot5 = baker.make("contents.MapSnapshot", map=map_obj, valid_from_chapter=5)
        baker.make("contents.MapSnapshot", map=map_obj, valid_from_chapter=10)

        result = MapService.get_for_chapter(map_obj.id, chapter_number=7)

        assert result["snapshot"].id == snapshot5.id

    def test_get_for_chapter_no_valid_snapshot(self):
        """유효한 스냅샷 없음"""
        map_obj = baker.make("contents.Map")
        baker.make("contents.MapSnapshot", map=map_obj, valid_from_chapter=5)

        result = MapService.get_for_chapter(map_obj.id, chapter_number=3)

        assert result["snapshot"] is None

    def test_get_for_chapter_with_layers_and_objects(self):
        """레이어와 오브젝트 포함 조회"""
        map_obj = baker.make("contents.Map")
        snapshot = baker.make("contents.MapSnapshot", map=map_obj, valid_from_chapter=1)
        layer = baker.make("contents.MapLayer", snapshot=snapshot, name="레이어1")
        baker.make("contents.MapObject", layer=layer, label="오브젝트1")
        baker.make("contents.MapObject", layer=layer, label="오브젝트2")

        result = MapService.get_for_chapter(map_obj.id, chapter_number=1)

        assert result["snapshot"].id == snapshot.id
        # prefetch 확인
        layers = list(result["snapshot"].layers.all())
        assert len(layers) == 1
        assert len(list(layers[0].map_objects.all())) == 2


class TestMapServiceFork:
    """MapService.fork_maps() 테스트"""

    def test_fork_maps(self):
        """지도 포크"""
        source_branch = baker.make("novels.Branch")
        target_branch = baker.make("novels.Branch")
        user = target_branch.author

        # 원본 지도 생성
        source_map = baker.make("contents.Map", branch=source_branch, name="세계 지도")
        source_snapshot = baker.make("contents.MapSnapshot", map=source_map, valid_from_chapter=1)
        source_layer = baker.make("contents.MapLayer", snapshot=source_snapshot)
        baker.make("contents.MapObject", layer=source_layer, label="도시")

        forked_maps = MapService.fork_maps(source_branch.id, target_branch.id, user)

        assert len(forked_maps) == 1
        forked_map = forked_maps[0]
        assert forked_map.branch == target_branch
        assert forked_map.source_map == source_map
        assert forked_map.name == "세계 지도"

        # 스냅샷, 레이어, 오브젝트 복사 확인
        forked_snapshots = forked_map.snapshots.all()
        assert forked_snapshots.count() == 1
        forked_layers = forked_snapshots[0].layers.all()
        assert forked_layers.count() == 1
        assert forked_layers[0].map_objects.count() == 1
