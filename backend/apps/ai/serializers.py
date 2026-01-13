"""
AI Serializers - Request/Response validation for AI endpoints.
"""

from rest_framework import serializers


class WikiSuggestionRequestSerializer(serializers.Serializer):
    """위키 제안 요청"""

    text = serializers.CharField(
        min_length=10,
        max_length=10000,
        help_text="분석할 텍스트 (10자 이상)",
    )


class WikiSuggestionItemSerializer(serializers.Serializer):
    """위키 제안 항목"""

    name = serializers.CharField(help_text="엔트리 이름")
    description = serializers.CharField(help_text="간단한 설명")


class WikiSuggestionResponseSerializer(serializers.Serializer):
    """위키 제안 응답"""

    data = WikiSuggestionItemSerializer(many=True)


class ConsistencyCheckRequestSerializer(serializers.Serializer):
    """일관성 검사 요청"""

    chapter_id = serializers.IntegerField(
        min_value=1,
        help_text="검사할 회차 ID",
    )


class ConsistencyCheckResponseSerializer(serializers.Serializer):
    """일관성 검사 응답"""

    consistent = serializers.BooleanField(help_text="일관성 여부")
    issues = serializers.ListField(
        child=serializers.CharField(),
        help_text="발견된 문제점 목록",
    )


class AskRequestSerializer(serializers.Serializer):
    """RAG 질문 요청"""

    question = serializers.CharField(
        min_length=5,
        max_length=1000,
        help_text="질문 내용 (5자 이상)",
    )


class AskResponseSerializer(serializers.Serializer):
    """RAG 질문 응답"""

    answer = serializers.CharField(help_text="AI 응답")


class ChunkTaskRequestSerializer(serializers.Serializer):
    """청킹 태스크 요청"""

    chapter_id = serializers.IntegerField(
        min_value=1,
        required=False,
        help_text="청킹할 회차 ID (선택)",
    )


class ChunkTaskResponseSerializer(serializers.Serializer):
    """청킹 태스크 응답"""

    task_id = serializers.CharField(help_text="Celery 태스크 ID")
    status = serializers.CharField(help_text="태스크 상태")
