"""
TDD: WikiEntry, WikiSnapshot, WikiTagDefinition 모델 테스트
RED → GREEN → REFACTOR
"""

import pytest
from django.db import IntegrityError
from model_bakery import baker


pytestmark = pytest.mark.django_db


class TestWikiEntryModel:
    """WikiEntry 모델 테스트"""

    def test_create_wiki_entry(self):
        """위키 엔트리 생성 테스트"""
        branch = baker.make("novels.Branch")
        wiki = baker.make(
            "contents.WikiEntry",
            branch=branch,
            name="테스트 캐릭터",
            image_url="https://example.com/char.jpg",
            first_appearance=1,
            hidden_note="작가 노트",
        )

        assert wiki.id is not None
        assert wiki.branch == branch
        assert wiki.name == "테스트 캐릭터"
        assert wiki.image_url == "https://example.com/char.jpg"
        assert wiki.first_appearance == 1
        assert wiki.hidden_note == "작가 노트"
        assert wiki.ai_metadata is None
        assert wiki.source_wiki is None

    def test_wiki_entry_unique_name_per_branch(self):
        """같은 브랜치에서 위키 이름 중복 불가"""
        branch = baker.make("novels.Branch")
        baker.make("contents.WikiEntry", branch=branch, name="캐릭터A")

        with pytest.raises(IntegrityError):
            baker.make("contents.WikiEntry", branch=branch, name="캐릭터A")

    def test_wiki_entry_same_name_different_branch(self):
        """다른 브랜치에서는 같은 이름 가능"""
        branch1 = baker.make("novels.Branch")
        branch2 = baker.make("novels.Branch")

        wiki1 = baker.make("contents.WikiEntry", branch=branch1, name="캐릭터A")
        wiki2 = baker.make("contents.WikiEntry", branch=branch2, name="캐릭터A")

        assert wiki1.name == wiki2.name
        assert wiki1.branch != wiki2.branch

    def test_wiki_entry_source_wiki_self_reference(self):
        """포크된 위키는 source_wiki 참조"""
        original_branch = baker.make("novels.Branch")
        forked_branch = baker.make("novels.Branch")

        original_wiki = baker.make("contents.WikiEntry", branch=original_branch, name="원본 캐릭터")
        forked_wiki = baker.make(
            "contents.WikiEntry",
            branch=forked_branch,
            name="원본 캐릭터",
            source_wiki=original_wiki,
        )

        assert forked_wiki.source_wiki == original_wiki
        assert forked_wiki.source_wiki.branch == original_branch

    def test_wiki_entry_ai_metadata_jsonfield(self):
        """ai_metadata JSONField 저장"""
        branch = baker.make("novels.Branch")
        wiki = baker.make(
            "contents.WikiEntry",
            branch=branch,
            name="AI 캐릭터",
            ai_metadata={"embedding": [0.1, 0.2, 0.3], "summary": "테스트 요약"},
        )

        assert wiki.ai_metadata["embedding"] == [0.1, 0.2, 0.3]
        assert wiki.ai_metadata["summary"] == "테스트 요약"

    def test_wiki_entry_str(self):
        """__str__ 메서드 테스트"""
        branch = baker.make("novels.Branch", name="메인 스토리")
        wiki = baker.make("contents.WikiEntry", branch=branch, name="주인공")

        assert str(wiki) == "메인 스토리 - 주인공"


class TestWikiSnapshotModel:
    """WikiSnapshot 모델 테스트"""

    def test_create_wiki_snapshot(self):
        """위키 스냅샷 생성 테스트"""
        wiki = baker.make("contents.WikiEntry")
        user = baker.make("users.User")

        snapshot = baker.make(
            "contents.WikiSnapshot",
            wiki_entry=wiki,
            content="## 캐릭터 설명\n첫 번째 스냅샷 내용",
            valid_from_chapter=1,
            contributor_type="USER",
            contributor=user,
        )

        assert snapshot.id is not None
        assert snapshot.wiki_entry == wiki
        assert snapshot.content == "## 캐릭터 설명\n첫 번째 스냅샷 내용"
        assert snapshot.valid_from_chapter == 1
        assert snapshot.contributor_type == "USER"
        assert snapshot.contributor == user

    def test_wiki_snapshot_unique_per_chapter(self):
        """같은 위키에서 같은 회차에 스냅샷 중복 불가"""
        wiki = baker.make("contents.WikiEntry")
        baker.make("contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=1)

        with pytest.raises(IntegrityError):
            baker.make("contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=1)

    def test_wiki_snapshot_multiple_chapters(self):
        """같은 위키에서 다른 회차 스냅샷 가능"""
        wiki = baker.make("contents.WikiEntry")

        snapshot1 = baker.make("contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=1)
        snapshot2 = baker.make("contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=5)
        snapshot3 = baker.make("contents.WikiSnapshot", wiki_entry=wiki, valid_from_chapter=10)

        assert snapshot1.valid_from_chapter == 1
        assert snapshot2.valid_from_chapter == 5
        assert snapshot3.valid_from_chapter == 10

    def test_wiki_snapshot_contributor_type_choices(self):
        """contributor_type은 USER 또는 AI"""
        wiki = baker.make("contents.WikiEntry")

        user_snapshot = baker.make(
            "contents.WikiSnapshot",
            wiki_entry=wiki,
            valid_from_chapter=1,
            contributor_type="USER",
        )
        ai_snapshot = baker.make(
            "contents.WikiSnapshot",
            wiki_entry=wiki,
            valid_from_chapter=2,
            contributor_type="AI",
        )

        assert user_snapshot.contributor_type == "USER"
        assert ai_snapshot.contributor_type == "AI"


class TestWikiTagDefinitionModel:
    """WikiTagDefinition 모델 테스트"""

    def test_create_wiki_tag_definition(self):
        """태그 정의 생성 테스트"""
        branch = baker.make("novels.Branch")
        tag = baker.make(
            "contents.WikiTagDefinition",
            branch=branch,
            name="인물",
            color="#FF5733",
            icon="user",
            description="등장인물 태그",
            display_order=1,
        )

        assert tag.id is not None
        assert tag.branch == branch
        assert tag.name == "인물"
        assert tag.color == "#FF5733"
        assert tag.icon == "user"
        assert tag.description == "등장인물 태그"
        assert tag.display_order == 1

    def test_wiki_tag_unique_name_per_branch(self):
        """같은 브랜치에서 태그 이름 중복 불가"""
        branch = baker.make("novels.Branch")
        baker.make("contents.WikiTagDefinition", branch=branch, name="인물")

        with pytest.raises(IntegrityError):
            baker.make("contents.WikiTagDefinition", branch=branch, name="인물")

    def test_wiki_tag_same_name_different_branch(self):
        """다른 브랜치에서는 같은 태그 이름 가능"""
        branch1 = baker.make("novels.Branch")
        branch2 = baker.make("novels.Branch")

        tag1 = baker.make("contents.WikiTagDefinition", branch=branch1, name="인물")
        tag2 = baker.make("contents.WikiTagDefinition", branch=branch2, name="인물")

        assert tag1.name == tag2.name
        assert tag1.branch != tag2.branch

    def test_wiki_tag_str(self):
        """__str__ 메서드 테스트"""
        branch = baker.make("novels.Branch", name="메인")
        tag = baker.make("contents.WikiTagDefinition", branch=branch, name="장소")

        assert str(tag) == "메인 - 장소"


class TestWikiEntryTagRelation:
    """WikiEntry와 WikiTagDefinition M2M 관계 테스트"""

    def test_wiki_entry_add_tags(self):
        """위키에 태그 추가"""
        branch = baker.make("novels.Branch")
        wiki = baker.make("contents.WikiEntry", branch=branch, name="캐릭터")

        tag1 = baker.make("contents.WikiTagDefinition", branch=branch, name="인물")
        tag2 = baker.make("contents.WikiTagDefinition", branch=branch, name="주인공")

        wiki.tags.add(tag1, tag2)

        assert wiki.tags.count() == 2
        assert tag1 in wiki.tags.all()
        assert tag2 in wiki.tags.all()

    def test_wiki_entry_remove_tag(self):
        """위키에서 태그 제거"""
        branch = baker.make("novels.Branch")
        wiki = baker.make("contents.WikiEntry", branch=branch, name="캐릭터")
        tag = baker.make("contents.WikiTagDefinition", branch=branch, name="인물")

        wiki.tags.add(tag)
        assert wiki.tags.count() == 1

        wiki.tags.remove(tag)
        assert wiki.tags.count() == 0

    def test_tag_definition_reverse_relation(self):
        """태그에서 위키 역참조"""
        branch = baker.make("novels.Branch")
        tag = baker.make("contents.WikiTagDefinition", branch=branch, name="인물")

        wiki1 = baker.make("contents.WikiEntry", branch=branch, name="캐릭터1")
        wiki2 = baker.make("contents.WikiEntry", branch=branch, name="캐릭터2")

        wiki1.tags.add(tag)
        wiki2.tags.add(tag)

        assert tag.wiki_entries.count() == 2
        assert wiki1 in tag.wiki_entries.all()
        assert wiki2 in tag.wiki_entries.all()
