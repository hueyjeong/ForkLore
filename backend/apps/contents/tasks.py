"""
Celery tasks for contents app.

Scheduled tasks for publishing chapters at their scheduled_at time.
"""

import json
import logging

import redis
from celery import shared_task
from django.conf import settings
from django.db import DatabaseError, transaction
from django.utils import timezone

from apps.contents.models import Chapter, ChapterStatus


@shared_task
def publish_scheduled_chapters() -> int:
    """
    예약된 시간(scheduled_at)이 지나 공개해야 하는 모든 SCHEDULED 상태의 챕터를 공개합니다.
    
    성공적으로 공개된 챕터 수를 반환합니다.
    
    Returns:
        int: 공개된 챕터의 수
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
        try:
            service.publish(chapter)
            published_count += 1
        except ValueError:
            # Chapter already published, skip
            pass

    return published_count


@shared_task
def sync_drafts_to_db() -> str:
    """
    Redis에 저장된 임시 초안(draft)들을 데이터베이스의 Chapter 레코드로 동기화한다.
    
    Redis에서 패턴 "draft:*:*"에 매칭되는 키를 스캔하여 각 키에서 branch_id와 chapter_id를 파싱하고,
    키가 ":new"로 끝나는 항목은 건너뛴다. Redis 값에서 title과 content를 읽어와 해당 Chapter가 존재하고
    상태가 DRAFT인 경우에만 제목·내용 및 파생 필드(content_html, word_count)를 업데이트한다.
    각 챕터 업데이트는 개별 트랜잭션으로 처리되며, 연속된 오류가 10회 발생하면 조기 종료한다.
    Redis 연결 오류가 발생하면 오류 메시지를 포함한 문자열을 반환한다.
    
    Returns:
        str: 동기화 결과 요약 문자열. 성공적으로 업데이트된 초안 수와 발생한 오류 수를 포함한다.
             형식 예시: "Synced {updated_count} drafts. Errors: {errors_count}"
    """
    from apps.contents.services import ChapterService

    logger = logging.getLogger(__name__)

    try:
        # Use django-redis to get the underlying Redis client
        # This ensures we use the same Redis connection as DraftService (via Django cache)
        from django_redis import get_redis_connection

        client = get_redis_connection("default")

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

                _prefix, branch_id_str, chapter_id_str = parts

                try:
                    branch_id = int(branch_id_str)
                    chapter_id = int(chapter_id_str)
                except ValueError:
                    logger.warning(f"Invalid IDs in key: {key_str}")
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
                    with transaction.atomic():
                        chapter = Chapter.objects.select_for_update().get(
                            id=chapter_id, branch_id=branch_id
                        )

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
            else:
                # Reset consecutive error counter after successful iteration
                errors_count = 0

        return f"Synced {updated_count} drafts. Errors: {errors_count}"

    except redis.RedisError as e:
        logger.error(f"Redis connection error: {str(e)}")
        return f"Redis error: {str(e)}"