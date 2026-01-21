import pytest
from django.core.cache import cache

from apps.novels.services import DraftService


@pytest.mark.django_db
class TestDraftService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = DraftService()
        cache.clear()

    def test_save_and_get_draft_new_chapter(self):
        """Test saving and retrieving a draft for a new chapter."""
        branch_id = 1
        title = "New Chapter"
        content = "Content here"

        # New signature: branch_id, chapter_id, title, content
        self.service.save_draft(branch_id, None, title, content)

        draft = self.service.get_draft(branch_id)
        assert draft is not None
        assert draft["title"] == title
        assert draft["content"] == content
        assert "updated_at" in draft

    def test_save_and_get_draft_existing_chapter(self):
        """Test saving and retrieving a draft for an existing chapter."""
        branch_id = 1
        chapter_id = 10
        title = "Edit Chapter"
        content = "Edited content"

        # New signature: branch_id, chapter_id, title, content
        self.service.save_draft(branch_id, chapter_id, title, content)

        draft = self.service.get_draft(branch_id, chapter_id)
        assert draft is not None
        assert draft["title"] == title
        assert draft["content"] == content

    def test_delete_draft(self):
        """Test deleting a draft."""
        branch_id = 1
        title = "To Delete"
        content = "..."

        self.service.save_draft(branch_id, None, title, content)
        assert self.service.get_draft(branch_id) is not None

        self.service.delete_draft(branch_id)
        assert self.service.get_draft(branch_id) is None

    def test_get_non_existent_draft(self):
        """Test retrieving a non-existent draft."""
        assert self.service.get_draft(999) is None
