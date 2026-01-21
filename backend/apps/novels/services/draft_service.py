from typing import Any

from django.core.cache import cache
from django.utils import timezone


class DraftService:
    """Service class for real-time draft auto-save using Redis."""

    TIMEOUT = 24 * 60 * 60  # 24 hours

    def _get_key(self, branch_id: int, chapter_id: int | None = None) -> str:
        """
        Generate cache key for draft.
        Format: draft:{branch_id}:{chapter_id} or draft:{branch_id}:new
        """
        if chapter_id:
            return f"draft:{branch_id}:{chapter_id}"
        return f"draft:{branch_id}:new"

    def save_draft(
        self,
        branch_id: int,
        chapter_id: int | None,
        title: str,
        content: str,
    ) -> None:
        """
        Save draft to cache.

        Args:
            branch_id: The branch ID
            chapter_id: Chapter ID (None for new chapter)
            title: Draft title
            content: Draft content
        """
        key = self._get_key(branch_id, chapter_id)
        data = {
            "title": title,
            "content": content,
            "updated_at": timezone.now(),
        }
        cache.set(key, data, self.TIMEOUT)

    def get_draft(
        self,
        branch_id: int,
        chapter_id: int | None = None,
    ) -> dict[str, Any] | None:
        """
        Retrieve draft from cache.

        Args:
            branch_id: The branch ID
            chapter_id: Optional chapter ID

        Returns:
            Dict containing title, content, updated_at OR None if not found
        """
        key = self._get_key(branch_id, chapter_id)
        return cache.get(key)

    def delete_draft(
        self,
        branch_id: int,
        chapter_id: int | None = None,
    ) -> None:
        """
        Delete draft from cache.

        Args:
            branch_id: The branch ID
            chapter_id: Optional chapter ID
        """
        key = self._get_key(branch_id, chapter_id)
        cache.delete(key)
