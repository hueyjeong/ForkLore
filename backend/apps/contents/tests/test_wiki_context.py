import pytest
from model_bakery import baker

from apps.contents.services import WikiService

pytestmark = pytest.mark.django_db


class TestWikiContextFiltering:
    """Test WikiService.list() with context filtering."""

    def test_list_wikis_filtered_by_chapter(self):
        """current_chapter 파라미터에 따른 위키 필터링 테스트"""
        branch = baker.make("novels.Branch")

        # Wiki A: first_appearance=1
        baker.make("contents.WikiEntry", branch=branch, name="Wiki A", first_appearance=1)

        # Wiki B: first_appearance=10
        baker.make("contents.WikiEntry", branch=branch, name="Wiki B", first_appearance=10)

        # Wiki C: first_appearance=None (Always visible)
        baker.make("contents.WikiEntry", branch=branch, name="Wiki C", first_appearance=None)

        # 1. current_chapter=1 -> Wiki A and Wiki C (Always visible)
        # Assuming Wiki A should be visible if first_appearance <= current_chapter
        results_ch1 = WikiService.list(branch_id=branch.id, current_chapter=1)

        # Checking IDs to be safe
        result_ids_ch1 = [w.id for w in results_ch1]
        assert 2 == len(result_ids_ch1)
        assert 0 == len(
            [w for w in results_ch1 if w.first_appearance is not None and w.first_appearance > 1]
        )

        # 2. current_chapter=10 -> Wiki A, Wiki B, Wiki C
        results_ch10 = WikiService.list(branch_id=branch.id, current_chapter=10)
        result_ids_ch10 = [w.id for w in results_ch10]

        assert 3 == len(result_ids_ch10)

        # 3. current_chapter=5 -> Wiki A, Wiki C
        results_ch5 = WikiService.list(branch_id=branch.id, current_chapter=5)
        result_ids_ch5 = [w.id for w in results_ch5]

        assert 2 == len(result_ids_ch5)

    def test_list_wikis_without_chapter_param(self):
        """current_chapter 파라미터가 없으면 모든 위키 반환"""
        branch = baker.make("novels.Branch")

        baker.make("contents.WikiEntry", branch=branch, first_appearance=1)
        baker.make("contents.WikiEntry", branch=branch, first_appearance=10)

        results = WikiService.list(branch_id=branch.id)

        assert len(results) == 2

    def test_list_wikis_future_chapter_is_hidden(self):
        """
        Ensure wikis whose first_appearance is after the current chapter are not returned by WikiService.list.
        """
        branch = baker.make("novels.Branch")

        # Wiki appears in chapter 10
        baker.make("contents.WikiEntry", branch=branch, first_appearance=10)

        # Viewing at chapter 9
        results = WikiService.list(branch_id=branch.id, current_chapter=9)

        assert len(results) == 0