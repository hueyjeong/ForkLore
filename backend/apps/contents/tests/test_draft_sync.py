import json
from unittest.mock import MagicMock, patch

import pytest
from model_bakery import baker

from apps.contents.models import Chapter, ChapterStatus
from apps.contents.tasks import sync_drafts_to_db


@pytest.mark.django_db
class TestDraftSync:
    def test_sync_drafts_success(self):
        """Test that drafts are successfully synced to DB."""
        # Setup existing chapter
        chapter = baker.make(
            Chapter, status=ChapterStatus.DRAFT, title="Old Title", content="Old Content"
        )

        # Prepare Redis data
        redis_key = f"draft:{chapter.branch.id}:{chapter.id}"
        new_data = {"title": "New Title", "content": "New Content"}

        # Mock Redis
        with patch("redis.from_url") as mock_redis_cls:
            mock_client = MagicMock()
            mock_redis_cls.return_value = mock_client

            # Mock scan_iter to return our key (bytes)
            mock_client.scan_iter.return_value = [redis_key.encode("utf-8")]

            # Mock get to return our data (bytes)
            mock_client.get.return_value = json.dumps(new_data).encode("utf-8")

            # Run task
            result = sync_drafts_to_db()

            # Verify DB updated
            chapter.refresh_from_db()
            assert chapter.title == "New Title"
            assert chapter.content == "New Content"
            assert "Synced 1 drafts" in result

    def test_sync_skip_published(self):
        """Test that published chapters are NOT updated."""
        chapter = baker.make(Chapter, status=ChapterStatus.PUBLISHED, title="Published Title")
        redis_key = f"draft:{chapter.branch.id}:{chapter.id}"

        with patch("redis.from_url") as mock_redis_cls:
            mock_client = MagicMock()
            mock_redis_cls.return_value = mock_client
            mock_client.scan_iter.return_value = [redis_key.encode("utf-8")]
            mock_client.get.return_value = json.dumps(
                {"title": "Hacked Title", "content": "Hacked Content"}
            ).encode("utf-8")

            sync_drafts_to_db()

            chapter.refresh_from_db()
            assert chapter.title == "Published Title"

    def test_skip_new_key(self):
        """Test that keys ending in :new are skipped."""
        redis_key = "draft:1:new"

        with patch("redis.from_url") as mock_redis_cls:
            mock_client = MagicMock()
            mock_redis_cls.return_value = mock_client
            mock_client.scan_iter.return_value = [redis_key.encode("utf-8")]

            sync_drafts_to_db()

            # Verify get() was never called for this key
            mock_client.get.assert_not_called()

    def test_handle_redis_error(self):
        """Test graceful handling of Redis errors."""
        import redis  # Import redis here or at top level

        with patch("redis.from_url") as mock_redis_cls:
            mock_client = MagicMock()
            mock_redis_cls.return_value = mock_client
            # Simulate Redis connection error
            mock_client.scan_iter.side_effect = redis.ConnectionError("Connection failed")

            result = sync_drafts_to_db()

            assert "Redis error" in result
