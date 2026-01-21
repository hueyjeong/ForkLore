"""
E2E Testing views.

Provides endpoints for E2E test setup and teardown.
Only enabled when E2E_ENABLED=True in settings (e2e.py).
"""

from django.conf import settings
from django.core.management import call_command
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
        """Truncate all app tables in correct order."""
        # Tables in dependency order (children first)
        tables = [
            # AI
            "ai_usage_logs",
            "chapter_chunks",
            # Interactions
            "coin_transactions",
            "wallets",
            "reports",
            "likes",
            "comments",
            "bookmarks",
            "reading_logs",
            "purchases",
            "subscriptions",
            # Contents
            "map_objects",
            "map_layers",
            "map_snapshots",
            "maps",
            "wiki_snapshots",
            "wiki_entries",
            "wiki_tag_definitions",
            "chapters",
            # Novels
            "branch_link_requests",
            "branch_votes",
            "branches",
            "novels",
            # Users
            "users",
        ]

        with connection.cursor() as cursor:
            # Disable FK checks for SQLite
            cursor.execute("PRAGMA foreign_keys = OFF;")

            for table in tables:
                try:
                    cursor.execute(f"DELETE FROM {table};")  # noqa: S608
                except Exception:
                    # Table might not exist in all configurations
                    pass

            # Re-enable FK checks
            cursor.execute("PRAGMA foreign_keys = ON;")
