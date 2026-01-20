from typing import Any

from django.core.cache import cache
from django.utils import timezone


class DraftService:
    """Service class for real-time draft auto-save using Redis."""

    TIMEOUT = 24 * 60 * 60  # 24 hours

    def _get_key(self, branch_id: int, chapter_id: int | None = None) -> str:
        """
        Constructs the cache key for a draft for a branch and optional chapter.
        
        Returns:
            key (str): Cache key in the form "draft:{branch_id}:{chapter_id}" if `chapter_id` is provided, otherwise "draft:{branch_id}:new".
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
        Save a draft for a branch (and optional chapter) to the cache.
        
        Stores a dictionary with keys `title`, `content`, and `updated_at` (current timezone-aware timestamp) under a generated cache key and sets its TTL to `TIMEOUT` seconds.
        
        Parameters:
            branch_id (int): Identifier of the branch the draft belongs to.
            chapter_id (int | None): Identifier of the chapter; pass `None` for a new (unsaved) chapter.
            title (str): Draft title.
            content (str): Draft content.
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
        Retrieve the draft for a branch and optional chapter from cache.
        
        Parameters:
            branch_id (int): Branch identifier.
            chapter_id (int | None): Chapter identifier; when None, returns the draft for a new (unsaved) chapter.
        
        Returns:
            dict[str, Any] | None: Dictionary with keys 'title', 'content', and 'updated_at' if found, `None` otherwise.
        """
        key = self._get_key(branch_id, chapter_id)
        return cache.get(key)

    def delete_draft(
        self,
        branch_id: int,
        chapter_id: int | None = None,
    ) -> None:
        """
        Remove a saved draft for a branch and optional chapter from the cache.
        
        Parameters:
            branch_id (int): ID of the branch owning the draft.
            chapter_id (int | None): Optional chapter ID; when None, targets the draft for a new (unsaved) chapter.
        """
        key = self._get_key(branch_id, chapter_id)
        cache.delete(key)