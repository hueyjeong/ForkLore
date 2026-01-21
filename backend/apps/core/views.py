"""
E2E Testing views.

Provides endpoints for E2E test setup and teardown.
Only enabled when E2E_ENABLED=True in settings (e2e.py).
"""

from django.conf import settings
from django.core.management import call_command
from pathlib import Path

from django.db import connection
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class E2EResetView(APIView):
    """
    Reset database and reseed with E2E test data.

    POST /api/e2e/reset

    Only available when E2E_ENABLED=True in Django settings.
    Returns 404 in production/test settings.
    """

    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        """Reset database and reseed with test data."""
        # Check if E2E mode is enabled
        if not getattr(settings, "E2E_ENABLED", False):
            return Response(
                {"error": "E2E endpoints are not enabled"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # Clear all data from tables (in correct order to respect FK constraints)
            self._truncate_tables()

            # Reseed with test data
            call_command("seed_e2e_data", verbosity=0)

            return Response(
                {
                    "success": True,
                    "message": "Database reset and reseeded successfully",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _truncate_tables(self) -> None:
        """Truncate all data tables for a clean E2E slate.

        Notes:
            The E2E environment uses a persisted SQLite DB file. Django's `flush`
            can intermittently fail under SQLite FK constraints and/or during
            permission/content-type recreation. For E2E we prefer a deterministic
            wipe that disables FK checks temporarily.
        """

        if connection.vendor == "sqlite":
            # E2E uses a file-based SQLite DB which can get into a state where
            # bulk deletes/flush intermittently fail with FK constraint errors.
            # The most reliable reset is: close connection → delete DB file → migrate.
            db_name = settings.DATABASES.get("default", {}).get("NAME")
            if db_name:
                db_path = Path(str(db_name))
                connection.close()
                if db_path.exists():
                    db_path.unlink()

            call_command("migrate", "--no-input", verbosity=0)
            return

        # Fallback for non-sqlite DBs.
        call_command("flush", "--no-input", "--inhibit-post-migrate", verbosity=0)
