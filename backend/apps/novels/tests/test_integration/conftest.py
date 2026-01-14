"""
Shared fixtures for novels integration tests.
"""

import json
from typing import Any

import pytest
from model_bakery import baker
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.users.models import User


def get_json(response: Response) -> Any:
    """Helper to parse JSON from response content."""
    return json.loads(response.content)


@pytest.fixture
def api_client() -> APIClient:
    """Return an API client instance."""
    return APIClient()


@pytest.fixture
def author(db: Any) -> User:
    """Create an author user."""
    user = User.objects.create_user(
        username="author@example.com",
        email="author@example.com",
        password="AuthorPass123!",
        nickname="author",
        role="AUTHOR",
    )
    return user


@pytest.fixture
def reader(db: Any) -> User:
    """Create a reader user."""
    user = User.objects.create_user(
        username="reader@example.com",
        email="reader@example.com",
        password="ReaderPass123!",
        nickname="reader",
        role="READER",
    )
    return user


@pytest.fixture
def author_client(api_client: APIClient, author: User) -> APIClient:
    """Return an authenticated API client for author."""
    api_client.force_authenticate(user=author)
    return api_client


@pytest.fixture
def reader_client(api_client: APIClient, reader: User) -> APIClient:
    """Return an authenticated API client for reader."""
    api_client.force_authenticate(user=reader)
    return api_client
