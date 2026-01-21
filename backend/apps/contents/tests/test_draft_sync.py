import json
from unittest.mock import MagicMock, patch

import pytest
from model_bakery import baker

from apps.contents.models import Chapter, ChapterStatus
from apps.contents.tasks import sync_drafts_to_db


@pytest.mark.django_db
class TestDraftSync:
    def test_sync_drafts_success(self):
        """
        레디스에 저장된 드래프트 데이터를 데이터베이스의 초안 챕터로 동기화하는 동작을 검증합니다.
        
        레디스에서 특정 챕터 키와 새 제목/내용을 반환하도록 모킹한 뒤 sync_drafts_to_db()를 실행하여,
        대상 챕터가 데이터베이스에서 새 제목과 내용으로 업데이트되고 결과 문자열에 "Synced 1 drafts"가 포함되는지를 확인합니다.
        """
        # Setup existing chapter
        chapter = baker.make(
            Chapter, status=ChapterStatus.DRAFT, title="Old Title", content="Old Content"
        )

        # Prepare Redis data
        redis_key = f"draft:{chapter.branch.id}:{chapter.id}"
        new_data = {"title": "New Title", "content": "New Content"}

        # Mock django-redis get_redis_connection
        with patch("django_redis.get_redis_connection") as mock_get_conn:
            mock_client = MagicMock()
            mock_get_conn.return_value = mock_client

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

        with patch("django_redis.get_redis_connection") as mock_get_conn:
            mock_client = MagicMock()
            mock_get_conn.return_value = mock_client
            mock_client.scan_iter.return_value = [redis_key.encode("utf-8")]
            mock_client.get.return_value = json.dumps(
                {"title": "Hacked Title", "content": "Hacked Content"}
            ).encode("utf-8")

            sync_drafts_to_db()

            chapter.refresh_from_db()
            assert chapter.title == "Published Title"

    def test_skip_new_key(self):
        """Redis 키가 ':new'로 끝나는 항목은 동기화 대상에서 제외되는지 검증한다."""
        redis_key = "draft:1:new"

        with patch("django_redis.get_redis_connection") as mock_get_conn:
            mock_client = MagicMock()
            mock_get_conn.return_value = mock_client
            mock_client.scan_iter.return_value = [redis_key.encode("utf-8")]

            sync_drafts_to_db()

            # Verify get() was never called for this key
            mock_client.get.assert_not_called()

    def test_handle_redis_error(self):
        """Redis 연결 오류가 발생했을 때 sync_drafts_to_db가 오류 메시지를 포함한 결과를 반환하며 예외 없이 처리되는지 검증한다."""
        import redis  # Import redis here or at top level

        with patch("django_redis.get_redis_connection") as mock_get_conn:
            mock_client = MagicMock()
            mock_get_conn.return_value = mock_client
            # Simulate Redis connection error
            mock_client.scan_iter.side_effect = redis.ConnectionError("Connection failed")

            result = sync_drafts_to_db()

            assert "Redis error" in result