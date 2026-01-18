import pytest
from model_bakery import baker
from apps.novels.models import Novel


@pytest.mark.django_db
class TestNovelModel:
    def test_novel_has_is_exclusive_field(self):
        novel = baker.make("novels.Novel", is_exclusive=True)
        assert novel.is_exclusive is True

        novel_default = baker.make("novels.Novel")
        assert novel_default.is_exclusive is False

    def test_novel_has_is_premium_field(self):
        novel = baker.make("novels.Novel", is_premium=True)
        assert novel.is_premium is True

        novel_default = baker.make("novels.Novel")
        assert novel_default.is_premium is False
