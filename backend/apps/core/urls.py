"""
URL configuration for E2E testing endpoints.

Only enabled when E2E_ENABLED=True in settings.
"""

from django.urls import path

from .views import E2EResetView

urlpatterns = [
    path("e2e/reset", E2EResetView.as_view(), name="e2e-reset"),
]
