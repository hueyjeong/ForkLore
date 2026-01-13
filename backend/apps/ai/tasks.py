"""
Celery Tasks - AI Integration
Background tasks for computationally intensive AI operations.
"""

import logging
from celery import shared_task

from apps.ai.services import ChunkingService
from apps.contents.models import Chapter


logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def create_chapter_chunks(self, chapter_id: int) -> dict:
    """
    Create chunks for a chapter asynchronously.

    This task:
    1. Fetches the chapter by ID
    2. Splits content into chunks
    3. Generates embeddings for each chunk
    4. Stores chunks in the database

    Args:
        chapter_id: ID of the chapter to process

    Returns:
        dict with chunk count and status
    """
    try:
        chapter = Chapter.objects.get(id=chapter_id)
    except Chapter.DoesNotExist:
        logger.error(f"Chapter {chapter_id} not found")
        return {"status": "error", "message": f"Chapter {chapter_id} not found"}

    service = ChunkingService()
    chunks = service.create_chunks(chapter)

    logger.info(f"Created {len(chunks)} chunks for chapter {chapter_id}")
    return {
        "status": "success",
        "chapter_id": chapter_id,
        "chunk_count": len(chunks),
    }


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def create_branch_chunks(self, branch_id: int) -> dict:
    """
    Create chunks for all chapters in a branch.

    Args:
        branch_id: ID of the branch to process

    Returns:
        dict with total chunk count and chapter count
    """
    from apps.novels.models import Branch

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        logger.error(f"Branch {branch_id} not found")
        return {"status": "error", "message": f"Branch {branch_id} not found"}

    chapters = Chapter.objects.filter(branch=branch)
    service = ChunkingService()

    total_chunks = 0
    processed_chapters = 0

    for chapter in chapters:
        chunks = service.create_chunks(chapter)
        total_chunks += len(chunks)
        processed_chapters += 1

    logger.info(
        f"Created {total_chunks} chunks for {processed_chapters} chapters in branch {branch_id}"
    )
    return {
        "status": "success",
        "branch_id": branch_id,
        "chapter_count": processed_chapters,
        "total_chunk_count": total_chunks,
    }
