from .base import *

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# N+1 Detection (optional - dev dependency)
try:
    import nplusone  # noqa: F401

    INSTALLED_APPS += ["nplusone.ext.django"]
    MIDDLEWARE.insert(0, "nplusone.ext.django.NPlusOneMiddleware")
    NPLUSONE_RAISE = True  # Raise error on N+1
    NPLUSONE_WHITELIST = [
        {"model": "contents.Map", "field": "branch"},
    ]
except ImportError:
    pass  # nplusone not installed
