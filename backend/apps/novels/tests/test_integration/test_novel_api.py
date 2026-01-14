"""
Integration tests for Novel API endpoints.
Tests the full HTTP request/response cycle.
"""

import json
from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.novels.models import Branch, Novel


def get_json(response: Response) -> Any:
    """Helper to parse JSON from response content."""
    return json.loads(response.content)


# =============================================================================
# Novel CRUD Tests
# =============================================================================


class TestNovelCRUD:
    """Tests for Novel CRUD operations"""

    def test_create_novel_creates_main_branch(
        self, author_client: APIClient, author: Any, db: Any
    ) -> None:
        """Creating a novel should automatically create a main branch."""
        url = reverse("novel-list")
        novel_data = {
            "title": "Test Novel",
            "description": "Test Description",
            "genre": "FANTASY",
        }
        response = author_client.post(url, novel_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = get_json(response)
        assert data["success"] is True

        # Verify main branch was created
        novel = Novel.objects.get(title="Test Novel")
        main_branch = Branch.objects.filter(novel=novel, is_main=True).first()
        assert main_branch is not None
        assert main_branch.author == author
        assert main_branch.visibility == "PUBLIC"

    def test_author_can_update_own_novel(
        self, author_client: APIClient, author: Any, db: Any
    ) -> None:
        """Author should be able to update their own novel."""
        # Create novel
        novel = Novel.objects.create(
            author=author,
            title="Original Title",
            genre="FANTASY",
        )

        # Update novel
        url = reverse("novel-detail", kwargs={"pk": novel.pk})
        update_data = {"title": "Updated Title"}
        response = author_client.patch(url, update_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        novel.refresh_from_db()
        assert novel.title == "Updated Title"

    def test_non_author_cannot_update_novel(
        self, reader_client: APIClient, author: Any, db: Any
    ) -> None:
        """Non-author should not be able to update novel."""
        # Create novel by author
        novel = Novel.objects.create(
            author=author,
            title="Original Title",
            genre="FANTASY",
        )

        # Try to update by reader
        url = reverse("novel-detail", kwargs={"pk": novel.pk})
        update_data = {"title": "Hacked Title"}
        response = reader_client.patch(url, update_data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        novel.refresh_from_db()
        assert novel.title == "Original Title"  # Title unchanged

    def test_list_novels(self, api_client: APIClient, author: Any, db: Any) -> None:
        """Should list all novels."""
        Novel.objects.create(author=author, title="Novel 1", genre="FANTASY")
        Novel.objects.create(author=author, title="Novel 2", genre="ROMANCE")

        url = reverse("novel-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = get_json(response)
        assert data["success"] is True
        assert len(data["data"]["results"]) >= 2
