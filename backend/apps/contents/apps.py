from django.apps import AppConfig


class ContentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.contents"
    verbose_name = "콘텐츠 관리"

    def ready(self):
        """
        Celery Beat 일정과 관련된 주기 작업을 데이터베이스에 동기화한다.
        
        django-celery-beat가 설치된 경우 5분(IntervalSchedule) 주기를 보장하고 이름이 "sync_drafts_to_db"인 PeriodicTask를 생성하거나 재사용하여 해당 작업이 데이터베이스에 존재하도록 한다. django-celery-beat가 설치되어 있지 않거나 마이그레이션(migrate/makemigrations) 중이면 아무 작업도 수행하지 않으며, 초기 마이그레이션 등으로 데이터베이스가 준비되지 않은 경우에도 예외를 발생시키지 않고 조용히 종료한다.
        """
        # Import here to avoid AppRegistryNotReady
        try:
            from django_celery_beat.models import IntervalSchedule, PeriodicTask
        except ImportError:
            # django-celery-beat not installed, skip
            return

        # Only run in main process, not in migrations
        import sys

        if "migrate" in sys.argv or "makemigrations" in sys.argv:
            return

        # Create or ensure the sync_drafts_to_db task exists in a safe, idempotent way
        from django.db import OperationalError, ProgrammingError, transaction

        try:
            with transaction.atomic():
                schedule, _ = IntervalSchedule.objects.get_or_create(
                    every=5,
                    period=IntervalSchedule.MINUTES,
                )
                # Use get_or_create so concurrent starts simply reuse the same task
                PeriodicTask.objects.get_or_create(
                    name="sync_drafts_to_db",
                    defaults={
                        "task": "apps.contents.tasks.sync_drafts_to_db",
                        "interval": schedule,
                        "enabled": True,
                    },
                )
        except (OperationalError, ProgrammingError):
            # Database might not be ready yet (e.g., during initial migration)
            return