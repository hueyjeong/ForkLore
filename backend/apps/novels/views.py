"""
Views for Novel API.

Endpoints:
- POST /api/v1/novels - Create novel
- GET /api/v1/novels - List novels
- GET /api/v1/novels/{id} - Retrieve novel
- PATCH /api/v1/novels/{id} - Update novel
- DELETE /api/v1/novels/{id} - Delete novel
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from common.pagination import StandardPagination
from common.permissions import IsOwnerOrReadOnly

from .models import Novel
from .services import NovelService
from .serializers import (
    NovelCreateSerializer,
    NovelDetailSerializer,
    NovelListSerializer,
    NovelUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="소설 목록 조회",
        description="공개된 소설 목록을 조회합니다.",
        parameters=[
            OpenApiParameter(name="genre", description="장르 필터"),
            OpenApiParameter(name="status", description="상태 필터"),
            OpenApiParameter(name="sort", description="정렬 (popular, latest, likes)"),
        ],
    ),
    retrieve=extend_schema(summary="소설 상세 조회"),
    create=extend_schema(
        summary="소설 생성", description="소설 생성 시 메인 브랜치가 자동 생성됩니다."
    ),
    partial_update=extend_schema(summary="소설 수정"),
    destroy=extend_schema(summary="소설 삭제 (소프트)"),
)
class NovelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Novel CRUD operations.
    """

    queryset = Novel.objects.filter(deleted_at__isnull=True)
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == "create":
            return NovelCreateSerializer
        elif self.action == "list":
            return NovelListSerializer
        elif self.action in ["update", "partial_update"]:
            return NovelUpdateSerializer
        return NovelDetailSerializer

    def get_queryset(self):
        """Apply filters and sorting."""
        queryset = super().get_queryset()

        # Filters
        genre = self.request.query_params.get("genre")
        novel_status = self.request.query_params.get("status")

        if genre:
            queryset = queryset.filter(genre=genre)
        if novel_status:
            queryset = queryset.filter(status=novel_status)

        # Sorting
        sort = self.request.query_params.get("sort", "latest")
        if sort == "popular":
            queryset = queryset.order_by("-total_view_count")
        elif sort == "likes":
            queryset = queryset.order_by("-total_like_count")
        else:  # latest
            queryset = queryset.order_by("-created_at")

        return queryset

    def create(self, request, *args, **kwargs):
        """Create a new novel with automatic main branch creation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = NovelService()
        novel = service.create(author=request.user, data=serializer.validated_data)

        output_serializer = NovelDetailSerializer(novel)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Update a novel (author only)."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Permission check
        if instance.author != request.user:
            return Response(
                {"detail": "소설 수정 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        service = NovelService()
        novel = service.update(
            novel_id=instance.id,
            author=request.user,
            data=serializer.validated_data,
        )

        output_serializer = NovelDetailSerializer(novel)
        return Response(output_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Soft-delete a novel (author only)."""
        instance = self.get_object()

        # Permission check
        if instance.author != request.user:
            return Response(
                {"detail": "소설 삭제 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        service = NovelService()
        service.delete(novel_id=instance.id, author=request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)
