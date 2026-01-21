"""
E2E Test Settings for ForkLore Backend.

Inherits from test.py and adds:
- SQLite file-based database (persisted for E2E tests)
- CORS configuration for Next.js frontend (localhost:3000)
- E2E_ENABLED flag for reset endpoint
"""

from pathlib import Path

from .test import *  # noqa: F401, F403

# Override database to use file-based SQLite (not in-memory)
# This allows the database to persist between Django restarts during E2E tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(__file__).resolve().parent.parent.parent / "e2e_test.sqlite3",
    }
}

# E2E-specific flag: enables /api/e2e/reset endpoint
E2E_ENABLED = True

# CORS Configuration for E2E testing
# Only allow Next.js dev server to make cross-origin requests
INSTALLED_APPS += ["corsheaders", "apps.core"]  # noqa: F405

# Insert CorsMiddleware before CommonMiddleware
# This is required for CORS preflight requests to work
MIDDLEWARE.insert(  # noqa: F405
    MIDDLEWARE.index("django.middleware.common.CommonMiddleware"),  # noqa: F405
    "corsheaders.middleware.CorsMiddleware",
)

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

# Allow credentials (cookies) for JWT authentication
CORS_ALLOW_CREDENTIALS = True

# Allowed hosts for E2E testing
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
