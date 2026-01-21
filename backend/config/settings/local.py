from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

INTERNAL_IPS = ["127.0.0.1"]

# N+1 Query Detection for development (optional - dev dependency)
try:
    import nplusone  # noqa: F401

    INSTALLED_APPS += ["nplusone.ext.django"]
    MIDDLEWARE.insert(1, "nplusone.ext.django.NPlusOneMiddleware")
    NPLUSONE_LOG_LEVEL = "WARNING"  # Log N+1 warnings in development
    NPLUSONE_RAISE = False  # Don't raise errors, just log
except ImportError:
    pass  # nplusone not installed (e.g., Docker without dev deps)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "nplusone": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
