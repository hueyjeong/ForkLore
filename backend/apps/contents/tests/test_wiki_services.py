"""
TDD: WikiService 테스트
RED → GREEN → REFACTOR
"""

import pytest
from django.core.exceptions import PermissionDenied
from model_bakery import baker

from apps.contents.models import WikiEntry, WikiTagDefinition
from apps.contents.services import WikiService

pytestmark = pytest.mark.django_db


class TestWikiServiceCreate:
    """WikiService.create() 테스트"""

    def test_create_wiki_entry(self):
        """위키 생성"""
        user = baker.make("users.User")
        branch = baker.make("novels.Branch", author=user)

        wiki = WikiService.create(
            branch_id=branch.id,
            user=user,
            name="주인공",
            image_url="https://example.com/hero.jpg",
            first_appearance=1,
            hidden_note="비밀 노트",
        )

        assert wiki.id is not None
        assert wiki.branch == branch
        assert wiki.name == "주인공"
        assert wiki.image_url == "https://example.com/hero.jpg"
        assert wiki.first_appearance == 1
        assert wiki.hidden_note == "비밀 노트"

    def test_create_wiki_entry_with_initial_snapshot(self):
        """위키 생성 시 초기 스냅샷 생성"""
        user = baker.make("users.User")
        branch = baker.make("novels.Branch", author=user)

        wiki = WikiService.create(
            branch_id=branch.id,
            user=user,
            name="주인공",
            initial_content="## 기본 설명\n주인공에 대한 설명",
        )

        assert wiki.snapshots.count() == 1
        snapshot = wiki.snapshots.first()
        assert snapshot.content == "## 기본 설명\n주인공에 대한 설명"
        assert snapshot.valid_from_chapter == 0
        assert snapshot.contributor == user
        assert snapshot.contributor_type == "USER"

    def test_create_wiki_entry_only_author(self):
        """브랜치 작가만 위키 생성 가능"""
        author = baker.make("users.User")
        other_user = baker.make("users.User")
        branch = baker.make("novels.Branch", author=author)

        with pytest.raises(PermissionDenied):
            WikiService.create(
                branch_id=branch.id,
                user=other_user,
                name="캐릭터",
            )

    def test_create_wiki_duplicate_name_error(self):
        """같은 브랜치에서 중복 이름 오류"""
        branch = baker.make("novels.Branch")
        user = branch.author
        WikiService.create(branch_id=branch.id, user=user, name="캐릭터A")

        with pytest.raises(ValueError) as exc_info:
            WikiService.create(branch_id=branch.id, user=user, name="캐릭터A")
        assert "이미 존재하는" in str(exc_info.value)


class TestWikiServiceUpdate:
    """WikiService.update() 테스트"""

    def test_update_wiki_entry(self):
        """위키 업데이트"""
        branch = baker.make("novels.Branch")
        wiki = baker.make("contents.WikiEntry", branch=branch, name="캐릭터")
        user = branch.author

        updated = WikiService.update(
            wiki_id=wiki.id,
            user=user,
            name="수정된 캐릭터",
            image_url="https://example.com/new.jpg",
        )

        assert updated.name == "수정된 캐릭터"
        assert updated.image_url == "https://example.com/new.jpg"

    def test_update_wiki_only_author(self):
        """브랜치 작가만 위키 수정 가능"""
        author = baker.make("users.User")
        other_user = baker.make("users.User")
        branch = baker.make("novels.Branch", author=author)
        wiki = baker.make("contents.WikiEntry", branch=branch)

        with pytest.raises(PermissionDenied):
            WikiService.update(wiki_id=wiki.id, user=other_user, name="수정")


class TestWikiServiceRetrieve:
    """WikiService.retrieve() 테스트"""

    def test_retrieve_wiki_entry(self):
        """위키 조회"""
        wiki = baker.make("contents.WikiEntry", name="테스트 캐릭터")

        result = WikiService.retrieve(wiki_id=wiki.id)

        assert result.id == wiki.id
        assert result.name == "테스트 캐릭터"

    def test_retrieve_nonexistent_wiki(self):
        """존재하지 않는 위키 조회"""
        with pytest.raises(ValueError) as exc_info:
            WikiService.retrieve(wiki_id=99999)
        assert "존재하지 않는" in str(exc_info.value)


class TestWikiServiceList:
    """WikiService.list() 테스트"""

    def test_list_wiki_entries_by_branch(self):
        """브랜치별 위키 목록"""
        branch = baker.make("novels.Branch")
        wiki1 = baker.make("contents.WikiEntry", branch=branch, name="A캐릭터")
        wiki2 = baker.make("contents.WikiEntry", branch=branch, name="B캐릭터")
        baker.make("contents.WikiEntry")  # 다른 브랜치

        result = WikiService.list(branch_id=branch.id)

        assert len(result) == 2
        assert wiki1 in result
        assert wiki2 in result

    def test_list_wiki_entries_with_tag_filter(self):
        """태그로 필터링"""
        branch = baker.make("novels.Branch")
        tag = baker.make("contents.WikiTagDefinition", branch=branch, name="인물")

        wiki1 = baker.make("contents.WikiEntry", branch=branch, name="캐릭터1")
        wiki2 = baker.make("contents.WikiEntry", branch=branch, name="캐릭터2")
        wiki3 = baker.make("contents.WikiEntry", branch=branch, name="장소1")

        wiki1.tags.add(tag)
        wiki2.tags.add(tag)

        result = WikiService.list(branch_id=branch.id, tag_id=tag.id)

        assert len(result) == 2
        assert wiki1 in result
        assert wiki2 in result
        assert wiki3 not in result


class TestWikiServiceDelete:
    """WikiService.delete() 테스트"""

    def test_delete_wiki_entry(self):
        """위키 삭제"""
        branch = baker.make("novels.Branch")
        wiki = baker.make("contents.WikiEntry", branch=branch)
        user = branch.author

        WikiService.delete(wiki_id=wiki.id, user=user)

        from apps.contents.models import WikiEntry

        assert not WikiEntry.objects.filter(id=wiki.id).exists()

    def test_delete_wiki_only_author(self):
        """브랜치 작가만 위키 삭제 가능"""
        author = baker.make("users.User")
        other_user = baker.make("users.User")
        branch = baker.make("novels.Branch", author=author)
        wiki = baker.make("contents.WikiEntry", branch=branch)

        with pytest.raises(PermissionDenied):
            WikiService.delete(wiki_id=wiki.id, user=other_user)


class TestWikiServiceTagManagement:
    """WikiService 태그 관리 테스트"""

    def test_add_tags_to_wiki(self):
        """위키에 태그 추가"""
        branch = baker.make("novels.Branch")
        wiki = baker.make("contents.WikiEntry", branch=branch)
        tag1 = baker.make("contents.WikiTagDefinition", branch=branch, name="인물")
        tag2 = baker.make("contents.WikiTagDefinition", branch=branch, name="주인공")
        user = branch.author

        WikiService.update_tags(wiki_id=wiki.id, user=user, tag_ids=[tag1.id, tag2.id])

        assert wiki.tags.count() == 2

    def test_set_tags_replaces_existing(self):
        """태그 설정 시 기존 태그 교체"""
        branch = baker.make("novels.Branch")
        wiki = baker.make("contents.WikiEntry", branch=branch)
        tag1 = baker.make("contents.WikiTagDefinition", branch=branch, name="인물")
        tag2 = baker.make("contents.WikiTagDefinition", branch=branch, name="주인공")
        tag3 = baker.make("contents.WikiTagDefinition", branch=branch, name="악역")
        user = branch.author

        wiki.tags.add(tag1, tag2)

        WikiService.update_tags(wiki_id=wiki.id, user=user, tag_ids=[tag3.id])

        assert wiki.tags.count() == 1
        assert tag3 in wiki.tags.all()
        assert tag1 not in wiki.tags.all()


class TestWikiTagDefinitionService:
    """WikiTagDefinitionService 테스트"""

    def test_create_tag_definition(self):
        """태그 정의 생성"""
        branch = baker.make("novels.Branch")
        user = branch.author

        tag = WikiService.create_tag(
            branch_id=branch.id,
            user=user,
            name="인물",
            color="#FF5733",
            icon="user",
            description="등장인물 태그",
        )

        assert tag.id is not None
        assert tag.name == "인물"
        assert tag.color == "#FF5733"

    def test_list_tag_definitions(self):
        """브랜치별 태그 목록"""
        branch = baker.make("novels.Branch")
        baker.make("contents.WikiTagDefinition", branch=branch, name="인물", display_order=1)
        baker.make("contents.WikiTagDefinition", branch=branch, name="장소", display_order=2)

        result = WikiService.list_tags(branch_id=branch.id)

        assert len(result) == 2
        assert result[0].name == "인물"
        assert result[1].name == "장소"

    def test_delete_tag_definition(self):
        """태그 삭제"""
        branch = baker.make("novels.Branch")
        tag = baker.make("contents.WikiTagDefinition", branch=branch, name="인물")
        user = branch.author

        WikiService.delete_tag(tag_id=tag.id, user=user)

        from apps.contents.models import WikiTagDefinition

        assert not WikiTagDefinition.objects.filter(id=tag.id).exists()


class TestWikiSnapshotService:
    """WikiService 스냅샷 관련 테스트"""

    def test_add_snapshot(self):
        """스냅샷 추가"""
        branch = baker.make("novels.Branch")
        wiki = baker.make("contents.WikiEntry", branch=branch)
        user = branch.author

        snapshot = WikiService.add_snapshot(
            wiki_id=wiki.id,
            user=user,
            content="## 회차 5부터 적용될 내용",
            valid_from_chapter=5,
        )

        assert snapshot.id is not None
        assert snapshot.wiki_entry == wiki
        assert snapshot.content == "## 회차 5부터 적용될 내용"
        assert snapshot.valid_from_chapter == 5
        assert snapshot.contributor == user

    def test_get_snapshot_for_chapter_exact_match(self):
        """정확히 일치하는 회차의 스냅샷 반환"""
        wiki = baker.make("contents.WikiEntry")
        baker.make("contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=1, content="초기")
        baker.make("contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=5, content="회차5")
        baker.make(
            "contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=10, content="회차10"
        )

        result = WikiService.get_snapshot_for_chapter(wiki_id=wiki.id, chapter_number=5)

        assert result.content == "회차5"
        assert result.valid_from_chapter == 5

    def test_get_snapshot_for_chapter_returns_latest_valid(self):
        """해당 회차 이하 중 가장 최신 스냅샷 반환"""
        wiki = baker.make("contents.WikiEntry")
        baker.make("contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=1, content="초기")
        baker.make("contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=5, content="회차5")
        baker.make(
            "contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=10, content="회차10"
        )

        # 회차 7은 스냅샷 5가 유효
        result = WikiService.get_snapshot_for_chapter(wiki_id=wiki.id, chapter_number=7)

        assert result.content == "회차5"
        assert result.valid_from_chapter == 5

    def test_get_snapshot_for_chapter_no_spoiler(self):
        """미래 회차의 스냅샷은 반환하지 않음 (스포일러 방지)"""
        wiki = baker.make("contents.WikiEntry")
        baker.make(
            "contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=10, content="미래 스포일러"
        )

        # 회차 3에서는 회차 10 스냅샷에 접근 불가
        result = WikiService.get_snapshot_for_chapter(wiki_id=wiki.id, chapter_number=3)

        assert result is None

    def test_get_snapshot_for_chapter_with_initial(self):
        """초기 스냅샷(0회차)이 있으면 항상 폴백"""
        wiki = baker.make("contents.WikiEntry")
        baker.make(
            "contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=0, content="초기 설정"
        )
        baker.make(
            "contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=10, content="회차10"
        )

        # 회차 5에서는 초기 스냅샷 반환
        result = WikiService.get_snapshot_for_chapter(wiki_id=wiki.id, chapter_number=5)

        assert result.content == "초기 설정"
        assert result.valid_from_chapter == 0

    def test_get_wiki_with_context(self):
        """문맥 인식 위키 조회 - 특정 회차 기준"""
        branch = baker.make("novels.Branch")
        wiki = baker.make("contents.WikiEntry", branch=branch, name="캐릭터")
        baker.make("contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=0, content="초기")
        baker.make(
            "contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=5, content="5화 이후"
        )

        result = WikiService.get_wiki_with_context(wiki_id=wiki.id, chapter_number=3)

        assert result["wiki"].name == "캐릭터"
        assert result["snapshot"].content == "초기"

        result2 = WikiService.get_wiki_with_context(wiki_id=wiki.id, chapter_number=7)
        assert result2["snapshot"].content == "5화 이후"


class TestWikiServiceFork:
    """WikiService.fork_wiki_entries() 테스트"""

    def test_fork_wiki_entries(self):
        """브랜치 포크 시 위키 복사"""
        source_branch = baker.make("novels.Branch")
        wiki1 = baker.make(
            "contents.WikiEntry",
            branch=source_branch,
            name="캐릭터1",
            image_url="https://example.com/1.jpg",
            first_appearance=1,
        )
        baker.make(
            "contents.WikiEntry",
            branch=source_branch,
            name="캐릭터2",
        )
        # 스냅샷도 복사
        baker.make(
            "contents.WikiSnapshot",
            wiki_entry=wiki1,
            valid_from_chapter=0,
            content="초기 내용",
        )
        baker.make(
            "contents.WikiSnapshot",
            wiki_entry=wiki1,
            valid_from_chapter=5,
            content="5화 내용",
        )

        target_branch = baker.make("novels.Branch")
        user = target_branch.author

        forked_wikis = WikiService.fork_wiki_entries(
            source_branch_id=source_branch.id,
            target_branch_id=target_branch.id,
            user=user,
        )

        assert len(forked_wikis) == 2

        # 복사된 위키 확인
        forked1 = WikiEntry.objects.filter(branch=target_branch, name="캐릭터1").first()
        assert forked1 is not None
        assert forked1.source_wiki == wiki1
        assert forked1.image_url == "https://example.com/1.jpg"
        assert forked1.first_appearance == 1

        # 스냅샷도 복사되었는지 확인
        assert forked1.snapshots.count() == 2

    def test_fork_wiki_entries_includes_tags(self):
        """포크 시 태그 정의도 복사"""
        source_branch = baker.make("novels.Branch")
        tag1 = baker.make(
            "contents.WikiTagDefinition",
            branch=source_branch,
            name="인물",
            color="#FF0000",
        )
        wiki = baker.make("contents.WikiEntry", branch=source_branch, name="캐릭터")
        wiki.tags.add(tag1)

        target_branch = baker.make("novels.Branch")
        user = target_branch.author

        WikiService.fork_wiki_entries(
            source_branch_id=source_branch.id,
            target_branch_id=target_branch.id,
            user=user,
        )

        # 태그 정의도 복사
        target_tags = WikiTagDefinition.objects.filter(branch=target_branch)
        assert target_tags.count() == 1
        assert target_tags.first().name == "인물"

        # 위키에 태그도 연결
        forked_wiki = WikiEntry.objects.filter(branch=target_branch, name="캐릭터").first()
        assert forked_wiki.tags.count() == 1

    def test_fork_empty_branch(self):
        """위키가 없는 브랜치 포크"""
        source_branch = baker.make("novels.Branch")
        target_branch = baker.make("novels.Branch")
        user = target_branch.author

        forked_wikis = WikiService.fork_wiki_entries(
            source_branch_id=source_branch.id,
            target_branch_id=target_branch.id,
            user=user,
        )

        assert len(forked_wikis) == 0
