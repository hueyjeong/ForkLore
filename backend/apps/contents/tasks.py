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
