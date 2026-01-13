"""
AI Services - Embedding, Chunking, Similarity Search, AI Features

Contains:
- TextChunker: 텍스트 분할 유틸
- EmbeddingService: Gemini 임베딩 생성
- ChunkingService: 회차 청크 생성
- SimilaritySearchService: pgvector 유사도 검색
- AIService: AI 기능 (위키 제안, 일관성 검사, RAG 질문응답)
"""

import json
import logging
import re
import time
from typing import Any

from django.conf import settings

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from apps.ai.models import ChapterChunk
from apps.contents.models import Chapter, WikiEntry
from apps.interactions.services import AIUsageService
from apps.users.models import User

logger = logging.getLogger(__name__)


class TextChunker:
    """텍스트를 청크로 분할하는 유틸리티 클래스."""

    @staticmethod
    def chunk_text(
        text: str,
        max_chunk_size: int = 1000,
        overlap: int = 100,
    ) -> list[str]:
        """
        텍스트를 청크로 분할합니다.

        Args:
            text: 분할할 텍스트
            max_chunk_size: 청크당 최대 글자 수
            overlap: 청크 간 오버랩 글자 수

        Returns:
            청크 리스트
        """
        if not text or not text.strip():
            return []

        text = text.strip()

        # 텍스트가 max_chunk_size보다 작으면 그대로 반환
        if len(text) <= max_chunk_size:
            return [text]

        # 문단 기준으로 먼저 분리
        paragraphs = re.split(r"\n\s*\n", text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            # 현재 청크에 문단 추가 시 max_chunk_size 초과하는지 확인
            if len(current_chunk) + len(para) + 1 <= max_chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                # 현재 청크 저장
                if current_chunk:
                    chunks.append(current_chunk)

                # 문단 자체가 max_chunk_size보다 큰 경우 문장 단위로 분할
                if len(para) > max_chunk_size:
                    sentences = re.split(r"(?<=[.!?。！？])\s*", para)
                    sentence_chunk = ""
                    for sentence in sentences:
                        if len(sentence_chunk) + len(sentence) + 1 <= max_chunk_size:
                            if sentence_chunk:
                                sentence_chunk += " " + sentence
                            else:
                                sentence_chunk = sentence
                        else:
                            if sentence_chunk:
                                chunks.append(sentence_chunk)
                            sentence_chunk = sentence
                    if sentence_chunk:
                        current_chunk = sentence_chunk
                    else:
                        current_chunk = ""
                else:
                    current_chunk = para

        # 마지막 청크 추가
        if current_chunk:
            chunks.append(current_chunk)

        # 오버랩 적용 (간단한 버전)
        if overlap > 0 and len(chunks) > 1:
            overlapped_chunks = []
            for i, chunk in enumerate(chunks):
                if i > 0 and len(chunks[i - 1]) >= overlap:
                    # 이전 청크의 마지막 부분을 현재 청크 앞에 추가
                    prefix = chunks[i - 1][-overlap:]
                    chunk = prefix + "..." + chunk
                overlapped_chunks.append(chunk)
            return overlapped_chunks

        return chunks


class EmbeddingService:
    """Gemini 임베딩 서비스."""

    def __init__(self) -> None:
        self.model = "models/text-embedding-004"
        self.dimension = 3072
        self._configure_api()

    def _configure_api(self) -> None:
        """Gemini API 설정."""
        if genai:
            api_key = getattr(settings, "GEMINI_API_KEY", None)
            if api_key:
                genai.configure(api_key=api_key)

    def embed(self, text: str, max_retries: int = 3) -> list[float]:
        """
        텍스트를 임베딩 벡터로 변환합니다.

        Args:
            text: 임베딩할 텍스트
            max_retries: 최대 재시도 횟수

        Returns:
            3072차원 임베딩 벡터
        """
        if not genai:
            logger.warning("google-generativeai not installed, returning zero vector")
            return [0.0] * self.dimension

        last_error = None
        for attempt in range(max_retries):
            try:
                result = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="retrieval_document",
                )
                return result["embedding"]
            except Exception as e:
                last_error = e
                logger.warning(f"Embedding attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))  # Exponential backoff

        logger.error(f"All embedding attempts failed: {last_error}")
        raise last_error

    def batch_embed(self, texts: list[str], max_retries: int = 3) -> list[list[float]]:
        """
        여러 텍스트를 배치로 임베딩합니다.

        Args:
            texts: 임베딩할 텍스트 리스트
            max_retries: 최대 재시도 횟수

        Returns:
            임베딩 벡터 리스트
        """
        embeddings = []
        for text in texts:
            embedding = self.embed(text, max_retries)
            embeddings.append(embedding)
        return embeddings


class ChunkingService:
    """회차 청킹 서비스."""

    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()
        self.max_chunk_size = 1000
        self.overlap = 100

    def create_chunks(self, chapter: Chapter) -> list[ChapterChunk]:
        """
        회차의 내용을 청크로 분할하고 임베딩을 생성합니다.

        Args:
            chapter: 청크를 생성할 회차

        Returns:
            생성된 ChapterChunk 리스트
        """
        # 기존 청크 삭제
        ChapterChunk.objects.filter(chapter=chapter).delete()

        # 텍스트 청킹
        chunks_text = TextChunker.chunk_text(
            chapter.content,
            max_chunk_size=self.max_chunk_size,
            overlap=self.overlap,
        )

        if not chunks_text:
            return []

        # 청크 생성 및 임베딩
        created_chunks = []
        for i, chunk_text in enumerate(chunks_text):
            try:
                embedding = self.embedding_service.embed(chunk_text)
            except Exception as e:
                logger.error(f"Failed to embed chunk {i}: {e}")
                embedding = None

            chunk = ChapterChunk.objects.create(
                chapter=chapter,
                chunk_index=i,
                content=chunk_text,
                embedding=embedding,
            )
            created_chunks.append(chunk)

        return created_chunks

    def create_chunks_batch(self, chapters: list[Chapter]) -> int:
        """
        여러 회차에 대해 청크를 생성합니다.

        Args:
            chapters: 청크를 생성할 회차 리스트

        Returns:
            생성된 총 청크 수
        """
        total_chunks = 0
        for chapter in chapters:
            chunks = self.create_chunks(chapter)
            total_chunks += len(chunks)
        return total_chunks


class SimilaritySearchService:
    """pgvector 기반 유사도 검색 서비스."""

    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()

    def search_by_text(
        self,
        branch_id: int,
        query: str,
        limit: int = 10,
    ) -> list[ChapterChunk]:
        """
        텍스트 쿼리로 유사한 청크를 검색합니다.

        Args:
            branch_id: 검색할 브랜치 ID
            query: 검색 쿼리 텍스트
            limit: 최대 결과 수

        Returns:
            유사한 ChapterChunk 리스트
        """
        try:
            query_embedding = self.embedding_service.embed(query)
            return self.search_by_embedding(branch_id, query_embedding, limit)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def search_by_embedding(
        self,
        branch_id: int,
        query_embedding: list[float],
        limit: int = 10,
    ) -> list[ChapterChunk]:
        """
        임베딩 벡터로 유사한 청크를 검색합니다.

        Args:
            branch_id: 검색할 브랜치 ID
            query_embedding: 쿼리 임베딩 벡터
            limit: 최대 결과 수

        Returns:
            유사한 ChapterChunk 리스트
        """
        # 브랜치에 속한 청크만 필터링
        base_queryset = ChapterChunk.objects.filter(chapter__branch_id=branch_id).select_related(
            "chapter"
        )

        try:
            # pgvector의 CosineDistance 사용 시도
            from pgvector.django import CosineDistance

            return list(
                base_queryset.annotate(
                    distance=CosineDistance("embedding", query_embedding)
                ).order_by("distance")[:limit]
            )
        except ImportError:
            # pgvector 없는 환경 (테스트)에서는 기본 쿼리 반환
            logger.warning("pgvector not available, returning basic query")
            return list(base_queryset[:limit])
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return list(base_queryset[:limit])


class AIService:
    """AI 기능 서비스 (위키 제안, 일관성 검사, RAG 질문응답)."""

    def __init__(self) -> None:
        self.search_service = SimilaritySearchService()
        self.model_name = "gemini-1.5-flash"
        self._configure_api()

    def _configure_api(self) -> None:
        """Gemini API 설정."""
        if genai:
            api_key = getattr(settings, "GEMINI_API_KEY", None)
            if api_key:
                genai.configure(api_key=api_key)

    def _check_usage_limit(self, user: User, action_type: str) -> None:
        """AI 사용량 한도 확인."""
        if not AIUsageService().can_use_ai(user, action_type):
            raise ValueError("일일 AI 사용 한도를 초과했습니다.")

    def _record_usage(self, user: User, action_type: str, token_count: int = 0) -> None:
        """AI 사용량 기록."""
        AIUsageService().increment(user=user, action_type=action_type, token_count=token_count)

    def _get_generative_model(self) -> Any:
        """Gemini 생성 모델 반환."""
        if not genai:
            raise ValueError("google-generativeai not installed")
        return genai.GenerativeModel(self.model_name)

    def suggest_wiki(
        self,
        branch_id: int,
        user: User,
        text: str,
    ) -> list[dict[str, Any]]:
        """
        텍스트에서 위키 엔트리 후보를 제안합니다.

        Args:
            branch_id: 브랜치 ID
            user: 요청 사용자
            text: 분석할 텍스트

        Returns:
            위키 제안 리스트 [{"name": "...", "description": "..."}]
        """
        self._check_usage_limit(user, "WIKI_SUGGEST")

        # 관련 청크 검색
        related_chunks = self.search_service.search_by_text(branch_id, text, limit=5)
        context = "\n".join([c.content for c in related_chunks]) if related_chunks else ""

        # 기존 위키 목록
        existing_wikis = list(
            WikiEntry.objects.filter(branch_id=branch_id).values_list("name", flat=True)
        )

        prompt = f"""다음 텍스트에서 새로운 위키 엔트리로 등록할 만한 캐릭터, 장소, 아이템, 개념 등을 추출해주세요.

기존 위키: {", ".join(existing_wikis) if existing_wikis else "없음"}

컨텍스트:
{context}

분석할 텍스트:
{text}

JSON 형식으로 응답해주세요:
[{{"name": "이름", "description": "간단한 설명"}}]

기존 위키와 중복되지 않는 새로운 엔트리만 제안해주세요."""

        try:
            model = self._get_generative_model()
            response = model.generate_content(prompt)
            result_text = response.text

            # JSON 파싱
            # 마크다운 코드 블록 제거
            result_text = re.sub(r"```json\s*", "", result_text)
            result_text = re.sub(r"```\s*", "", result_text)

            suggestions = json.loads(result_text.strip())

            self._record_usage(user, "WIKI_SUGGEST")
            return suggestions
        except Exception as e:
            logger.error(f"Wiki suggestion failed: {e}")
            return []

    def check_consistency(
        self,
        branch_id: int,
        chapter_id: int,
        user: User,
    ) -> dict[str, Any]:
        """
        회차의 설정 일관성을 검사합니다.

        Args:
            branch_id: 브랜치 ID
            chapter_id: 검사할 회차 ID
            user: 요청 사용자

        Returns:
            일관성 검사 결과 {"consistent": bool, "issues": [...]}
        """
        self._check_usage_limit(user, "CONSISTENCY_CHECK")

        try:
            chapter = Chapter.objects.get(id=chapter_id)
        except Chapter.DoesNotExist as e:
            raise ValueError("존재하지 않는 회차입니다.") from e

        # 관련 청크 검색
        related_chunks = self.search_service.search_by_text(
            branch_id, chapter.content[:500], limit=10
        )
        context = "\n".join([c.content for c in related_chunks]) if related_chunks else ""

        # 위키 정보
        wikis = WikiEntry.objects.filter(branch_id=branch_id).prefetch_related("snapshots")
        wiki_info = []
        for wiki in wikis[:20]:  # 상위 20개만
            snapshot = wiki.snapshots.order_by("-valid_from_chapter").first()
            if snapshot:
                wiki_info.append(f"- {wiki.name}: {snapshot.content[:200]}")

        prompt = f"""다음 회차 내용의 설정 일관성을 검사해주세요.

기존 컨텍스트 (이전 회차들):
{context}

위키 설정:
{chr(10).join(wiki_info) if wiki_info else "없음"}

검사할 회차 내용:
{chapter.content}

JSON 형식으로 응답해주세요:
{{"consistent": true/false, "issues": ["문제점1", "문제점2"]}}

일관성 문제가 없으면 {{"consistent": true, "issues": []}}로 응답해주세요."""

        try:
            model = self._get_generative_model()
            response = model.generate_content(prompt)
            result_text = response.text

            # 마크다운 코드 블록 제거
            result_text = re.sub(r"```json\s*", "", result_text)
            result_text = re.sub(r"```\s*", "", result_text)

            result = json.loads(result_text.strip())

            self._record_usage(user, "CONSISTENCY_CHECK")
            return result
        except Exception as e:
            logger.error(f"Consistency check failed: {e}")
            return {"consistent": True, "issues": [], "error": str(e)}

    def ask(
        self,
        branch_id: int,
        user: User,
        question: str,
    ) -> str:
        """
        RAG 기반으로 질문에 답변합니다.

        Args:
            branch_id: 브랜치 ID
            user: 요청 사용자
            question: 질문

        Returns:
            AI 응답
        """
        self._check_usage_limit(user, "ASK")

        # 관련 청크 검색
        related_chunks = self.search_service.search_by_text(branch_id, question, limit=5)
        context = "\n\n---\n\n".join([c.content for c in related_chunks]) if related_chunks else ""

        # 위키 정보
        wikis = WikiEntry.objects.filter(branch_id=branch_id)[:10]
        wiki_names = [w.name for w in wikis]

        prompt = f"""당신은 소설의 설정을 잘 알고 있는 AI 어시스턴트입니다.
다음 컨텍스트와 위키 정보를 바탕으로 질문에 답변해주세요.

위키 엔트리: {", ".join(wiki_names) if wiki_names else "없음"}

관련 컨텍스트:
{context if context else "관련 정보 없음"}

질문: {question}

소설의 설정에 기반하여 답변해주세요. 컨텍스트에 없는 정보는 "해당 정보가 없습니다"라고 답변해주세요."""

        try:
            model = self._get_generative_model()
            response = model.generate_content(prompt)

            self._record_usage(user, "ASK")
            return response.text
        except Exception as e:
            logger.error(f"Ask failed: {e}")
            raise ValueError(f"AI 응답 생성에 실패했습니다: {e}") from e
