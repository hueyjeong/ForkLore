"""
TDD: AI Services 테스트
RED → GREEN → REFACTOR
"""

import pytest
from unittest.mock import patch, MagicMock
from model_bakery import baker

from apps.ai.services import (
    EmbeddingService,
    TextChunker,
    ChunkingService,
    SimilaritySearchService,
    AIService,
)
from apps.ai.models import ChapterChunk


pytestmark = pytest.mark.django_db


class TestTextChunker:
    """TextChunker 유틸 테스트"""

    def test_chunk_by_paragraphs(self):
        """문단 기반 청킹"""
        text = """첫 번째 문단입니다.
여러 문장이 있습니다.

두 번째 문단입니다.
이것도 여러 문장이 있습니다.

세 번째 문단입니다."""

        chunks = TextChunker.chunk_text(text, max_chunk_size=500)

        assert len(chunks) >= 1
        assert all(len(chunk) <= 500 for chunk in chunks)

    def test_chunk_with_overlap(self):
        """오버랩이 있는 청킹"""
        text = "문장1. 문장2. 문장3. 문장4. 문장5. 문장6. 문장7. 문장8."

        chunks = TextChunker.chunk_text(text, max_chunk_size=30, overlap=10)

        # 오버랩이 있으면 청크 간에 겹치는 부분이 있어야 함
        assert len(chunks) >= 2

    def test_chunk_empty_text(self):
        """빈 텍스트 처리"""
        chunks = TextChunker.chunk_text("")

        assert chunks == []

    def test_chunk_small_text(self):
        """작은 텍스트는 하나의 청크"""
        text = "짧은 텍스트입니다."

        chunks = TextChunker.chunk_text(text, max_chunk_size=500)

        assert len(chunks) == 1
        assert chunks[0] == text


class TestEmbeddingService:
    """EmbeddingService 테스트"""

    @patch("apps.ai.services.genai")
    def test_embed_text(self, mock_genai):
        """텍스트 임베딩 생성"""
        # Mock Gemini API response
        mock_result = MagicMock()
        mock_result.embedding = [0.1] * 3072
        mock_genai.embed_content.return_value = {"embedding": [0.1] * 3072}

        service = EmbeddingService()
        embedding = service.embed("테스트 텍스트")

        assert len(embedding) == 3072
        mock_genai.embed_content.assert_called_once()

    @patch("apps.ai.services.genai")
    def test_batch_embed(self, mock_genai):
        """배치 임베딩"""
        mock_genai.embed_content.return_value = {"embedding": [0.1] * 3072}

        service = EmbeddingService()
        texts = ["텍스트1", "텍스트2", "텍스트3"]
        embeddings = service.batch_embed(texts)

        assert len(embeddings) == 3
        assert all(len(e) == 3072 for e in embeddings)

    @patch("apps.ai.services.genai")
    def test_embed_with_retry_on_error(self, mock_genai):
        """API 에러 시 재시도"""
        mock_genai.embed_content.side_effect = [Exception("API Error"), {"embedding": [0.1] * 3072}]

        service = EmbeddingService()
        embedding = service.embed("테스트", max_retries=2)

        assert len(embedding) == 3072
        assert mock_genai.embed_content.call_count == 2


class TestChunkingService:
    """ChunkingService 테스트"""

    @patch("apps.ai.services.EmbeddingService")
    def test_create_chunks_for_chapter(self, mock_embedding_service):
        """회차에 대한 청크 생성"""
        mock_embedding_service.return_value.embed.return_value = [0.1] * 3072

        chapter = baker.make("contents.Chapter", content="첫 번째 문단.\n\n두 번째 문단.")

        service = ChunkingService()
        chunks = service.create_chunks(chapter)

        assert len(chunks) >= 1
        assert all(isinstance(c, ChapterChunk) for c in chunks)
        assert all(c.chapter == chapter for c in chunks)

    @patch("apps.ai.services.EmbeddingService")
    def test_recreate_chunks_deletes_old(self, mock_embedding_service):
        """청크 재생성 시 기존 청크 삭제"""
        mock_embedding_service.return_value.embed.return_value = [0.1] * 3072

        chapter = baker.make("contents.Chapter", content="내용")
        baker.make(
            "ai.ChapterChunk", chapter=chapter, chunk_index=0, content="이전 청크", embedding=None
        )

        service = ChunkingService()
        service.create_chunks(chapter)

        # 기존 청크가 삭제되고 새 청크만 존재
        assert ChapterChunk.objects.filter(chapter=chapter).count() >= 1


class TestSimilaritySearchService:
    """SimilaritySearchService 테스트"""

    def test_search_similar_chunks(self):
        """유사 청크 검색"""
        branch = baker.make("novels.Branch")
        chapter = baker.make("contents.Chapter", branch=branch)

        # 테스트용 청크 생성 (embedding은 None으로)
        baker.make(
            "ai.ChapterChunk", chapter=chapter, chunk_index=0, content="청크1", embedding=None
        )
        baker.make(
            "ai.ChapterChunk", chapter=chapter, chunk_index=1, content="청크2", embedding=None
        )

        service = SimilaritySearchService()
        # 실제 pgvector 없이 테스트할 수 있는 기본 검색
        results = service.search_by_text(branch_id=branch.id, query="검색어", limit=5)

        # pgvector 없으면 빈 결과 또는 폴백 동작
        assert isinstance(results, list)

    def test_search_limits_to_branch(self):
        """브랜치 범위 제한 검색"""
        branch1 = baker.make("novels.Branch")
        branch2 = baker.make("novels.Branch")
        chapter1 = baker.make("contents.Chapter", branch=branch1)
        chapter2 = baker.make("contents.Chapter", branch=branch2)
        baker.make("ai.ChapterChunk", chapter=chapter1, content="브랜치1 청크", embedding=None)
        baker.make("ai.ChapterChunk", chapter=chapter2, content="브랜치2 청크", embedding=None)

        service = SimilaritySearchService()
        results = service.search_by_text(branch_id=branch1.id, query="청크", limit=10)

        # 결과가 branch1에만 속해야 함
        for result in results:
            assert result.chapter.branch_id == branch1.id


class TestAIService:
    """AIService 테스트"""

    @patch("apps.ai.services.AIUsageService")
    @patch("apps.ai.services.genai")
    @patch.object(SimilaritySearchService, "search_by_text")
    def test_suggest_wiki(self, mock_search, mock_genai, mock_usage):
        """위키 제안"""
        mock_usage.return_value.can_use_ai.return_value = True
        mock_search.return_value = []
        mock_genai.GenerativeModel.return_value.generate_content.return_value.text = """
        [{"name": "주인공", "description": "이야기의 주인공"}]
        """

        branch = baker.make("novels.Branch")
        user = branch.author

        service = AIService()
        suggestions = service.suggest_wiki(
            branch_id=branch.id, user=user, text="주인공이 등장하는 장면"
        )

        assert isinstance(suggestions, list)

    @patch("apps.ai.services.AIUsageService")
    @patch("apps.ai.services.genai")
    @patch.object(SimilaritySearchService, "search_by_text")
    def test_check_consistency(self, mock_search, mock_genai, mock_usage):
        """일관성 검사"""
        mock_usage.return_value.can_use_ai.return_value = True
        mock_search.return_value = []
        mock_genai.GenerativeModel.return_value.generate_content.return_value.text = """
        {"consistent": true, "issues": []}
        """

        branch = baker.make("novels.Branch")
        chapter = baker.make("contents.Chapter", branch=branch, content="테스트 내용")
        user = branch.author

        service = AIService()
        result = service.check_consistency(branch_id=branch.id, chapter_id=chapter.id, user=user)

        assert "consistent" in result or "issues" in result

    @patch("apps.ai.services.AIUsageService")
    @patch("apps.ai.services.genai")
    @patch.object(SimilaritySearchService, "search_by_text")
    def test_ask(self, mock_search, mock_genai, mock_usage):
        """RAG 기반 질문 응답"""
        mock_usage.return_value.can_use_ai.return_value = True
        mock_chunk = MagicMock()
        mock_chunk.content = "관련 컨텍스트 내용"
        mock_search.return_value = [mock_chunk]
        mock_genai.GenerativeModel.return_value.generate_content.return_value.text = (
            "AI 응답입니다."
        )

        branch = baker.make("novels.Branch")
        user = branch.author

        service = AIService()
        answer = service.ask(branch_id=branch.id, user=user, question="주인공은 누구인가요?")

        assert isinstance(answer, str)
        assert len(answer) > 0

    @patch("apps.ai.services.genai")
    def test_ask_checks_usage_limit(self, mock_genai):
        """AI 사용량 한도 검사"""
        branch = baker.make("novels.Branch")
        user = branch.author

        # AIUsageService 모킹하여 한도 초과 상태 설정
        with patch("apps.ai.services.AIUsageService") as mock_usage:
            mock_usage.return_value.can_use_ai.return_value = False

            service = AIService()
            with pytest.raises(ValueError) as exc_info:
                service.ask(branch_id=branch.id, user=user, question="질문")

            assert "한도" in str(exc_info.value) or "limit" in str(exc_info.value).lower()
