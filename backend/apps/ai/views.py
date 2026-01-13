"""
AI Views - API endpoints for AI features.

Endpoints:
- POST /branches/{id}/ai/wiki-suggestions - 위키 제안
- POST /branches/{id}/ai/consistency-check - 일관성 검사
- POST /branches/{id}/ai/ask - RAG 질문응답
- POST /branches/{id}/ai/create-chunks - 청킹 태스크 (Celery)
"""

import logging
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.ai.serializers import (
    WikiSuggestionRequestSerializer,
    WikiSuggestionResponseSerializer,
    ConsistencyCheckRequestSerializer,
    ConsistencyCheckResponseSerializer,
    AskRequestSerializer,
    AskResponseSerializer,
    ChunkTaskRequestSerializer,
    ChunkTaskResponseSerializer,
)
from apps.ai.services import AIService
from apps.ai.tasks import create_chapter_chunks, create_branch_chunks
from apps.novels.models import Branch


logger = logging.getLogger(__name__)


@extend_schema_view(
    wiki_suggestions=extend_schema(
        request=WikiSuggestionRequestSerializer,
        responses={200: WikiSuggestionResponseSerializer},
        summary="위키 제안",
        description="텍스트를 분석하여 새 위키 엔트리 후보를 제안합니다.",
        tags=["AI"],
    ),
    consistency_check=extend_schema(
        request=ConsistencyCheckRequestSerializer,
        responses={200: ConsistencyCheckResponseSerializer},
        summary="일관성 검사",
        description="회차의 설정 일관성을 검사합니다.",
        tags=["AI"],
    ),
    ask=extend_schema(
        request=AskRequestSerializer,
        responses={200: AskResponseSerializer},
        summary="RAG 질문응답",
        description="소설 설정에 대해 RAG 기반으로 질문에 답변합니다.",
        tags=["AI"],
    ),
    create_chunks=extend_schema(
        request=ChunkTaskRequestSerializer,
        responses={202: ChunkTaskResponseSerializer},
        summary="청킹 태스크 생성",
        description="회차 또는 브랜치 전체를 청킹하는 백그라운드 태스크를 생성합니다.",
        tags=["AI"],
    ),
)
class AIViewSet(GenericViewSet):
    """
    AI 기능 ViewSet.

    브랜치 컨텍스트에서 AI 기능을 제공합니다.
    """

    permission_classes = [IsAuthenticated]

    def get_branch(self, branch_id: int) -> Branch:
        """브랜치 조회 with 권한 검사."""
        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return None

        # 권한 검사: 작가 또는 협력자만 접근 가능
        if branch.author != self.request.user:
            # TODO: 협력자 검사 추가
            return None

        return branch

    @action(detail=False, methods=["post"], url_path="wiki-suggestions")
    def wiki_suggestions(self, request, **kwargs):
        """위키 제안 API."""
        branch_pk = kwargs.get("branch_pk")
        branch = self.get_branch(branch_pk)
        if not branch:
            return Response(
                {"error": "브랜치를 찾을 수 없거나 접근 권한이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WikiSuggestionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = AIService()
            suggestions = service.suggest_wiki(
                branch_id=branch.id,
                user=request.user,
                text=serializer.validated_data["text"],
            )
            return Response({"data": suggestions})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except Exception as e:
            logger.error(f"Wiki suggestion failed: {e}")
            return Response(
                {"error": "위키 제안 생성에 실패했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"], url_path="consistency-check")
    def consistency_check(self, request, **kwargs):
        """일관성 검사 API."""
        branch_pk = kwargs.get("branch_pk")
        branch = self.get_branch(branch_pk)
        if not branch:
            return Response(
                {"error": "브랜치를 찾을 수 없거나 접근 권한이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ConsistencyCheckRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = AIService()
            result = service.check_consistency(
                branch_id=branch.id,
                chapter_id=serializer.validated_data["chapter_id"],
                user=request.user,
            )
            return Response(result)
        except ValueError as e:
            error_msg = str(e)
            if "한도" in error_msg:
                return Response({"error": error_msg}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Consistency check failed: {e}")
            return Response(
                {"error": "일관성 검사에 실패했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"], url_path="ask")
    def ask(self, request, **kwargs):
        """RAG 질문응답 API."""
        branch_pk = kwargs.get("branch_pk")
        branch = self.get_branch(branch_pk)
        if not branch:
            return Response(
                {"error": "브랜치를 찾을 수 없거나 접근 권한이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AskRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = AIService()
            answer = service.ask(
                branch_id=branch.id,
                user=request.user,
                question=serializer.validated_data["question"],
            )
            return Response({"answer": answer})
        except ValueError as e:
            error_msg = str(e)
            if "한도" in error_msg:
                return Response({"error": error_msg}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Ask failed: {e}")
            return Response(
                {"error": "AI 응답 생성에 실패했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"], url_path="create-chunks")
    def create_chunks(self, request, **kwargs):
        """청킹 태스크 생성 API."""
        branch_pk = kwargs.get("branch_pk")
        branch = self.get_branch(branch_pk)
        if not branch:
            return Response(
                {"error": "브랜치를 찾을 수 없거나 접근 권한이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ChunkTaskRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        chapter_id = serializer.validated_data.get("chapter_id")

        if chapter_id:
            # 특정 회차만 청킹
            task = create_chapter_chunks.delay(chapter_id)
        else:
            # 브랜치 전체 청킹
            task = create_branch_chunks.delay(branch.id)

        return Response(
            {"task_id": task.id, "status": "pending"},
            status=status.HTTP_202_ACCEPTED,
        )
