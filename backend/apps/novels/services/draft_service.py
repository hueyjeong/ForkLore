from typing import Any

from django.core.cache import cache
from django.utils import timezone


class DraftService:
    """Service class for real-time draft auto-save using Redis."""

    TIMEOUT = 24 * 60 * 60  # 24 hours

    def _get_key(self, branch_id: int, chapter_id: int | None = None) -> str:
        """
        드래프트 저장에 사용되는 캐시 키를 생성합니다.
        
        chapter_id가 주어지면 'draft:{branch_id}:{chapter_id}', 주어지지 않으면 'draft:{branch_id}:new' 형식의 키를 생성합니다.
        
        Parameters:
            branch_id: 드래프트가 속한 브랜치의 식별자.
            chapter_id: 챕터 식별자; 생략(또는 None)하면 새 챕터용 키를 생성합니다.
        
        Returns:
            생성된 캐시 키 문자열 (예: `draft:42:3` 또는 `draft:42:new`).
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
        초안(title·content)을 캐시에 저장한다.
        
        저장된 항목에는 `title`, `content`, `updated_at` 타임스탬프가 포함되며, 클래스의 `TIMEOUT`(24시간) 동안 유지된다.
        
        Parameters:
            branch_id (int): 초안이 속한 브랜치의 식별자.
            chapter_id (int | None): 대상 챕터의 식별자. `None`이면 새 챕터용 임시 초안으로 저장된다.
            title (str): 초안 제목.
            content (str): 초안 내용.
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
        브랜치(및 선택적 챕터)에 대한 임시 저장된 초안 데이터를 가져옵니다.
        
        Parameters:
            branch_id (int): 초안이 속한 브랜치의 ID.
            chapter_id (int | None): 챕터 ID; 제공하지 않으면 새 챕터용 임시 초안으로 취급됩니다.
        
        Returns:
            dict[str, Any] | None: 키 `title`, `content`, `updated_at`를 포함한 초안 사전 또는 존재하지 않으면 `None`.
        """
        key = self._get_key(branch_id, chapter_id)
        return cache.get(key)

    def delete_draft(
        self,
        branch_id: int,
        chapter_id: int | None = None,
    ) -> None:
        """
        캐시에서 지정한 브랜치 및 선택적 챕터의 임시 저장(드래프트)을 삭제한다.
        
        Parameters:
            branch_id (int): 삭제할 드래프트가 속한 브랜치의 ID.
            chapter_id (int | None): 챕터 ID가 주어지면 해당 챕터의 드래프트를 삭제하고,
                주어지지 않으면 새 글용 드래프트 키를 대상으로 삭제한다.
        """
        key = self._get_key(branch_id, chapter_id)
        cache.delete(key)