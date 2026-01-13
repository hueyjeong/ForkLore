"""
TDD: AI Views 테스트
RED → GREEN → REFACTOR
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from model_bakery import baker

from apps.ai.views import AIViewSet


pytestmark = pytest.mark.django_db


class TestAIViewSetBase:
    """Base test class with common setup."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.client = APIClient()
        self.user = baker.make("users.User")
        self.novel = baker.make("novels.Novel", author=self.user)
        self.branch = baker.make("novels.Branch", novel=self.novel, author=self.user, is_main=True)
        self.client.force_authenticate(user=self.user)


class TestWikiSuggestions(TestAIViewSetBase):
    """위키 제안 API 테스트"""

    def get_url(self):
        return f"/api/v1/branches/{self.branch.id}/ai/wiki-suggestions/"

    @patch("apps.ai.views.AIService")
    def test_wiki_suggestions_success(self, mock_service):
        """위키 제안 성공"""
        mock_service.return_value.suggest_wiki.return_value = [
            {"name": "주인공", "description": "이야기의 주인공"}
        ]

        response = self.client.post(
            self.get_url(),
            {"text": "주인공이 마을을 걸어가고 있다."},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.data
        assert isinstance(response.data["data"], list)

    def test_wiki_suggestions_unauthorized(self):
        """인증되지 않은 요청"""
        self.client.logout()

        response = self.client.post(
            self.get_url(),
            {"text": "테스트 텍스트입니다."},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("apps.ai.views.AIService")
    def test_wiki_suggestions_text_too_short(self, mock_service):
        """텍스트가 너무 짧은 경우"""
        response = self.client.post(
            self.get_url(),
            {"text": "짧음"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("apps.ai.views.AIService")
    def test_wiki_suggestions_rate_limit(self, mock_service):
        """AI 사용량 한도 초과"""
        mock_service.return_value.suggest_wiki.side_effect = ValueError(
            "일일 AI 사용 한도를 초과했습니다."
        )

        response = self.client.post(
            self.get_url(),
            {"text": "충분히 긴 텍스트입니다."},
            format="json",
        )

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_wiki_suggestions_wrong_branch(self):
        """다른 사용자의 브랜치에 접근"""
        other_user = baker.make("users.User")
        other_branch = baker.make("novels.Branch", author=other_user)

        response = self.client.post(
            f"/api/v1/branches/{other_branch.id}/ai/wiki-suggestions/",
            {"text": "충분히 긴 텍스트입니다."},
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestConsistencyCheck(TestAIViewSetBase):
    """일관성 검사 API 테스트"""

    def get_url(self):
        return f"/api/v1/branches/{self.branch.id}/ai/consistency-check/"

    @patch("apps.ai.views.AIService")
    def test_consistency_check_success(self, mock_service):
        """일관성 검사 성공"""
        chapter = baker.make("contents.Chapter", branch=self.branch, content="테스트 내용")
        mock_service.return_value.check_consistency.return_value = {
            "consistent": True,
            "issues": [],
        }

        response = self.client.post(
            self.get_url(),
            {"chapter_id": chapter.id},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "consistent" in response.data

    @patch("apps.ai.views.AIService")
    def test_consistency_check_with_issues(self, mock_service):
        """일관성 문제 발견"""
        chapter = baker.make("contents.Chapter", branch=self.branch, content="테스트 내용")
        mock_service.return_value.check_consistency.return_value = {
            "consistent": False,
            "issues": ["캐릭터 설정 불일치", "시간대 오류"],
        }

        response = self.client.post(
            self.get_url(),
            {"chapter_id": chapter.id},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["consistent"] is False
        assert len(response.data["issues"]) == 2

    def test_consistency_check_missing_chapter_id(self):
        """chapter_id 누락"""
        response = self.client.post(
            self.get_url(),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAsk(TestAIViewSetBase):
    """RAG 질문응답 API 테스트"""

    def get_url(self):
        return f"/api/v1/branches/{self.branch.id}/ai/ask/"

    @patch("apps.ai.views.AIService")
    def test_ask_success(self, mock_service):
        """질문 응답 성공"""
        mock_service.return_value.ask.return_value = "주인공의 이름은 홍길동입니다."

        response = self.client.post(
            self.get_url(),
            {"question": "주인공의 이름은 무엇인가요?"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "answer" in response.data
        assert response.data["answer"] == "주인공의 이름은 홍길동입니다."

    def test_ask_question_too_short(self):
        """질문이 너무 짧은 경우"""
        response = self.client.post(
            self.get_url(),
            {"question": "뭐?"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("apps.ai.views.AIService")
    def test_ask_rate_limit(self, mock_service):
        """AI 사용량 한도 초과"""
        mock_service.return_value.ask.side_effect = ValueError("일일 AI 사용 한도를 초과했습니다.")

        response = self.client.post(
            self.get_url(),
            {"question": "충분히 긴 질문입니다."},
            format="json",
        )

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


class TestCreateChunks(TestAIViewSetBase):
    """청킹 태스크 API 테스트"""

    def get_url(self):
        return f"/api/v1/branches/{self.branch.id}/ai/create-chunks/"

    @patch("apps.ai.views.create_branch_chunks")
    def test_create_chunks_for_branch(self, mock_task):
        """브랜치 전체 청킹"""
        mock_task.delay.return_value.id = "mock-task-id"

        response = self.client.post(
            self.get_url(),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.data
        mock_task.delay.assert_called_once_with(self.branch.id)

    @patch("apps.ai.views.create_chapter_chunks")
    def test_create_chunks_for_chapter(self, mock_task):
        """특정 회차 청킹"""
        chapter = baker.make("contents.Chapter", branch=self.branch)
        mock_task.delay.return_value.id = "mock-task-id"

        response = self.client.post(
            self.get_url(),
            {"chapter_id": chapter.id},
            format="json",
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        mock_task.delay.assert_called_once_with(chapter.id)
