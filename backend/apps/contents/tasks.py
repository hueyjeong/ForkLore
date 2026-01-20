"""
Celery tasks for contents app.

Scheduled tasks for publishing chapters at their scheduled_at time.
"""

import json
import logging

import redis
from celery import shared_task
from django.conf import settings
from django.db import DatabaseError
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
    from apps.contents.services import ChapterService

    now = timezone.now()
    service = ChapterService()

    # Find all scheduled chapters ready to publish
    chapters_to_publish = Chapter.objects.filter(
        status=ChapterStatus.SCHEDULED,
        scheduled_at__lte=now,
    ).select_related("branch")

    published_count = 0

    for chapter in chapters_to_publish:
        # Use service.publish() to ensure version increment and proper logic
        chapter.status = ChapterStatus.PUBLISHED
        chapter.published_at = now
        chapter.save()
        # Manually trigger version update through the service method
        branch = chapter.branch
        branch.chapter_count = F("chapter_count") + 1
        branch.version = F("version") + 1
        branch.save(update_fields=["chapter_count", "version"])
        published_count += 1

    return published_count


@shared_task
def sync_drafts_to_db() -> str:
    """
    Sync Redis drafts to the database.
    Finds all keys matching 'draft:*:*' and updates corresponding Chapter objects.
    Skips keys ending in ':new'.
    """
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
                    # Wrap each chapter update in its own transaction
                    # This ensures partial success - if one chapter fails,
                    # others that succeeded remain saved
                    from django.db import transaction

                    with transaction.atomic():
                        chapter = Chapter.objects.get(id=chapter_id)

                        # Constraint: Only update if status is DRAFT
                        if chapter.status != ChapterStatus.DRAFT:
                            continue

                        # Check if update is needed
                        if chapter.title != title or chapter.content != content:
                            chapter.title = title
                            chapter.content = content

                            # Update derived fields using service logic
                            chapter.content_html = service.convert_markdown(content)
                            chapter.word_count = service.calculate_word_count(content)

                            chapter.save()
                            updated_count += 1

                except Chapter.DoesNotExist:
                    # Silently ignore if chapter was deleted from DB
                    continue

            except (
                redis.RedisError,
                ValueError,
                TypeError,
                json.JSONDecodeError,
                DatabaseError,
            ) as e:
                logger.error(f"Error processing key {key_str}: {str(e)}")
                errors_count += 1
                if errors_count >= 10:
                    logger.error("Too many errors while syncing drafts, aborting early.")
                    break
                continue

        return f"Synced {updated_count} drafts. Errors: {errors_count}"

    except redis.RedisError as e:
        logger.error(f"Redis connection error: {str(e)}")
        return f"Redis error: {str(e)}"
