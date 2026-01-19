"""
Celery tasks for contents app.

Scheduled tasks for publishing chapters at their scheduled_at time.
"""

from celery import shared_task
from django.db.models import F
from django.utils import timezone

from apps.contents.models import Chapter, ChapterStatus


@shared_task
def publish_scheduled_chapters() -> int:
    """
    Publish all chapters whose scheduled_at time has passed.

    This task should be run periodically (e.g., every minute) via celery-beat.
    It finds all SCHEDULED chapters with scheduled_at <= now and publishes them.

    Returns:
        int: Number of chapters published
    """
    now = timezone.now()

    # Find all scheduled chapters ready to publish
    chapters_to_publish = Chapter.objects.filter(
        status=ChapterStatus.SCHEDULED,
        scheduled_at__lte=now,
    ).select_related("branch")

    published_count = 0
    branch_counts = {}

    for chapter in chapters_to_publish:
        chapter.status = ChapterStatus.PUBLISHED
        chapter.published_at = now
        chapter.save(update_fields=["status", "published_at", "updated_at"])

        # Track branch increments
        branch_id = chapter.branch_id
        branch_counts[branch_id] = branch_counts.get(branch_id, 0) + 1
        published_count += 1

    # Update branch chapter_counts using F() for atomicity
    from apps.novels.models import Branch

    for branch_id, count in branch_counts.items():
        Branch.objects.filter(id=branch_id).update(chapter_count=F("chapter_count") + count)

    return published_count


@shared_task
def sync_drafts_to_db() -> str:
    """
    Sync Redis drafts to the database.
    Finds all keys matching 'draft:*:*' and updates corresponding Chapter objects.
    Skips keys ending in ':new'.
    """
    import json
    import logging

    import redis
    from django.conf import settings

    from apps.contents.services import ChapterService

    logger = logging.getLogger(__name__)

    try:
        # Initialize Redis client
        redis_url = getattr(settings, "CELERY_BROKER_URL", "redis://localhost:6379/0")
        client = redis.from_url(redis_url)

        # Pattern matching
        pattern = "draft:*:*"

        updated_count = 0
        errors_count = 0
        service = ChapterService()

        # Use scan_iter for memory efficiency
        for key in client.scan_iter(match=pattern):
            key_str = key.decode("utf-8")

            # Filter out keys ending in :new
            if key_str.endswith(":new"):
                continue

            try:
                # Parse branch_id and chapter_id from key
                # Expected: draft:{branch_id}:{chapter_id}
                parts = key_str.split(":")
                if len(parts) != 3:
                    continue

                _prefix, _branch_id, chapter_id_str = parts

                try:
                    chapter_id = int(chapter_id_str)
                except ValueError:
                    logger.warning(f"Invalid chapter_id in key: {key_str}")
                    continue

                # Get data from Redis
                data_raw = client.get(key)
                if not data_raw:
                    continue

                try:
                    data = json.loads(data_raw)
                except json.JSONDecodeError:
                    continue

                title = data.get("title")
                content = data.get("content")

                if title is None or content is None:
                    continue

                try:
                    chapter = Chapter.objects.get(id=chapter_id)

                    # Constraint: Only update if status is DRAFT
                    if chapter.status != ChapterStatus.DRAFT:
                        continue

                    # Check if update is needed
                    if chapter.title != title or chapter.content != content:
                        chapter.title = title
                        chapter.content = content

                        # Update derived fields using service logic
                        chapter.content_html = service._convert_markdown(content)
                        chapter.word_count = service._calculate_word_count(content)

                        chapter.save()
                        updated_count += 1

                except Chapter.DoesNotExist:
                    # Silently ignore if chapter was deleted from DB
                    continue

            except Exception as e:
                logger.error(f"Error processing key {key_str}: {str(e)}")
                errors_count += 1
                continue

        return f"Synced {updated_count} drafts. Errors: {errors_count}"

    except redis.RedisError as e:
        logger.error(f"Redis connection error: {str(e)}")
        return f"Redis error: {str(e)}"
