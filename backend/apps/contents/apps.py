from django.apps import AppConfig


class ContentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.contents"
    verbose_name = "콘텐츠 관리"

    def ready(self):
        """Sync Celery Beat schedules to database."""
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

        # Create or update the sync_drafts_to_db task
        try:
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=5,
                period=IntervalSchedule.MINUTES,
            )
            PeriodicTask.objects.update_or_create(
                name="sync_drafts_to_db",
                defaults={
                    "task": "apps.contents.tasks.sync_drafts_to_db",
                    "interval": schedule,
                    "enabled": True,
                },
            )
        except Exception:
            # Database might not be ready yet (e.g., during initial migration)
            pass
