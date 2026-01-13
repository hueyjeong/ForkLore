"""
ViewSets for contents app.

Contains views for:
- ChapterViewSet: Nested under branches for list/create
- ChapterDetailViewSet: For update/delete/publish/schedule
- WikiEntryViewSet: Nested under branches for list/create
- WikiEntryDetailViewSet: For retrieve/update/delete
- WikiTagViewSet: Nested under branches for list/create
- WikiSnapshotViewSet: Nested under wikis for list/create
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, extend_schema_view

from common.pagination import StandardPagination

from apps.novels.models import Branch
from apps.contents.models import Chapter, ChapterStatus, WikiEntry, WikiTagDefinition
from apps.contents.services import ChapterService, WikiService
from apps.contents.serializers import (
    ChapterCreateSerializer,
    ChapterDetailSerializer,
    ChapterListSerializer,
    ChapterUpdateSerializer,
    ChapterScheduleSerializer,
    WikiEntryListSerializer,
    WikiEntryDetailSerializer,
    WikiEntryCreateSerializer,
    WikiEntryUpdateSerializer,
    WikiTagDefinitionSerializer,
    WikiTagDefinitionCreateSerializer,
    WikiSnapshotSerializer,
    WikiSnapshotCreateSerializer,
    WikiTagUpdateSerializer,
)


class IsBranchAuthor:
    """Permission check for branch author."""

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        # obj is Chapter
        return obj.branch.author == request.user


@extend_schema_view(
    list=extend_schema(
        summary="회차 목록 조회",
        description="브랜치의 회차 목록을 조회합니다.",
        tags=["Chapters"],
    ),
    create=extend_schema(
        summary="회차 생성",
        description="새 회차를 생성합니다 (임시저장 상태).",
        tags=["Chapters"],
    ),
    retrieve=extend_schema(
        summary="회차 상세 조회",
        description="회차 상세 정보를 조회합니다.",
        tags=["Chapters"],
    ),
)
class ChapterViewSet(viewsets.ViewSet):
    """
    ViewSet for chapters nested under branches.

    Routes:
    - GET /branches/{branch_id}/chapters/ - List chapters
    - GET /branches/{branch_id}/chapters/{chapter_number}/ - Get chapter detail
    - POST /branches/{branch_id}/chapters/ - Create chapter
    """

    pagination_class = StandardPagination

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request, branch_pk=None):
        """List chapters for a branch."""
        service = ChapterService()

        # Check if user is branch author (can see drafts)
        try:
            branch = Branch.objects.get(pk=branch_pk)
        except Branch.DoesNotExist:
            return Response(
                {"success": False, "message": "브랜치를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        is_author = request.user.is_authenticated and branch.author == request.user
        chapters = service.list(branch_id=branch_pk, published_only=not is_author)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(chapters, request)
        serializer = ChapterListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, branch_pk=None, pk=None):
        """Get chapter detail by chapter_number."""
        service = ChapterService()

        try:
            chapter_number = int(pk)
        except (ValueError, TypeError):
            return Response(
                {"success": False, "message": "잘못된 회차 번호입니다.", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        chapter = service.retrieve(branch_id=branch_pk, chapter_number=chapter_number)

        if not chapter:
            return Response(
                {"success": False, "message": "회차를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check access permissions
        if chapter.status != ChapterStatus.PUBLISHED:
            if not request.user.is_authenticated or chapter.branch.author != request.user:
                return Response(
                    {"success": False, "message": "회차를 찾을 수 없습니다.", "data": None},
                    status=status.HTTP_404_NOT_FOUND,
                )

        serializer = ChapterDetailSerializer(chapter)
        return Response(serializer.data)

    def create(self, request, branch_pk=None):
        """Create a new chapter."""
        # Get branch and verify ownership
        try:
            branch = Branch.objects.get(pk=branch_pk)
        except Branch.DoesNotExist:
            return Response(
                {"success": False, "message": "브랜치를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        if branch.author != request.user:
            return Response(
                {"success": False, "message": "권한이 없습니다.", "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ChapterCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "유효성 검사 실패", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = ChapterService()
        chapter = service.create(
            branch=branch,
            title=serializer.validated_data["title"],
            content=serializer.validated_data["content"],
            access_type=serializer.validated_data.get("access_type", "FREE"),
            price=serializer.validated_data.get("price", 0),
        )

        response_serializer = ChapterDetailSerializer(chapter)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    retrieve=extend_schema(
        summary="회차 상세 조회 (ID)",
        description="회차 ID로 상세 정보를 조회합니다.",
        tags=["Chapters"],
    ),
    partial_update=extend_schema(
        summary="회차 수정",
        description="회차를 수정합니다.",
        tags=["Chapters"],
    ),
    destroy=extend_schema(
        summary="회차 삭제",
        description="회차를 삭제합니다.",
        tags=["Chapters"],
    ),
)
class ChapterDetailViewSet(viewsets.ViewSet):
    """
    ViewSet for chapter operations by chapter ID.

    Routes:
    - GET /chapters/{id}/ - Get chapter by ID
    - PATCH /chapters/{id}/ - Update chapter
    - DELETE /chapters/{id}/ - Delete chapter
    - POST /chapters/{id}/publish/ - Publish chapter
    - POST /chapters/{id}/schedule/ - Schedule chapter
    """

    def get_permissions(self):
        if self.action in ["retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def _get_chapter(self, pk):
        """Helper to get chapter by ID."""
        try:
            return Chapter.objects.select_related("branch").get(pk=pk)
        except Chapter.DoesNotExist:
            return None

    def _check_author(self, chapter, user):
        """Check if user is the branch author."""
        return chapter.branch.author == user

    def retrieve(self, request, pk=None):
        """Get chapter by ID."""
        chapter = self._get_chapter(pk)
        if not chapter:
            return Response(
                {"success": False, "message": "회차를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ChapterDetailSerializer(chapter)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        """Update a chapter."""
        chapter = self._get_chapter(pk)
        if not chapter:
            return Response(
                {"success": False, "message": "회차를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not self._check_author(chapter, request.user):
            return Response(
                {"success": False, "message": "권한이 없습니다.", "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ChapterUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "유효성 검사 실패", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = ChapterService()
        try:
            updated = service.update(chapter=chapter, **serializer.validated_data)
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = ChapterDetailSerializer(updated)
        return Response(response_serializer.data)

    def destroy(self, request, pk=None):
        """Delete a chapter."""
        chapter = self._get_chapter(pk)
        if not chapter:
            return Response(
                {"success": False, "message": "회차를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not self._check_author(chapter, request.user):
            return Response(
                {"success": False, "message": "권한이 없습니다.", "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )

        chapter.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="회차 발행",
        description="임시저장 회차를 즉시 발행합니다.",
        tags=["Chapters"],
    )
    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """Publish a draft chapter."""
        chapter = self._get_chapter(pk)
        if not chapter:
            return Response(
                {"success": False, "message": "회차를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not self._check_author(chapter, request.user):
            return Response(
                {"success": False, "message": "권한이 없습니다.", "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )

        service = ChapterService()
        try:
            published = service.publish(chapter=chapter)
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ChapterDetailSerializer(published)
        return Response(serializer.data)

    @extend_schema(
        summary="회차 예약 발행",
        description="회차를 예약 발행 설정합니다.",
        tags=["Chapters"],
    )
    @action(detail=True, methods=["post"])
    def schedule(self, request, pk=None):
        """Schedule a chapter for future publication."""
        chapter = self._get_chapter(pk)
        if not chapter:
            return Response(
                {"success": False, "message": "회차를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not self._check_author(chapter, request.user):
            return Response(
                {"success": False, "message": "권한이 없습니다.", "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ChapterScheduleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "유효성 검사 실패", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = ChapterService()
        try:
            scheduled = service.schedule(
                chapter=chapter,
                scheduled_at=serializer.validated_data["scheduled_at"],
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = ChapterDetailSerializer(scheduled)
        return Response(response_serializer.data)


# =============================================================================
# Wiki ViewSets
# =============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="위키 목록 조회",
        description="브랜치의 위키 목록을 조회합니다.",
        tags=["Wiki"],
    ),
    create=extend_schema(
        summary="위키 생성",
        description="새 위키 엔트리를 생성합니다.",
        tags=["Wiki"],
    ),
)
class WikiEntryViewSet(viewsets.ViewSet):
    """
    ViewSet for wiki entries nested under branches.

    Routes:
    - GET /branches/{branch_id}/wikis/ - List wikis
    - POST /branches/{branch_id}/wikis/ - Create wiki
    """

    pagination_class = StandardPagination

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request, branch_pk=None):
        """List wiki entries for a branch."""
        tag_id = request.query_params.get("tag")
        tag_id = int(tag_id) if tag_id else None

        wikis = WikiService.list(branch_id=branch_pk, tag_id=tag_id)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(wikis, request)
        serializer = WikiEntryListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def create(self, request, branch_pk=None):
        """Create a new wiki entry."""
        serializer = WikiEntryCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "유효성 검사 실패", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            wiki = WikiService.create(
                branch_id=branch_pk,
                user=request.user,
                name=serializer.validated_data["name"],
                image_url=serializer.validated_data.get("image_url", ""),
                first_appearance=serializer.validated_data.get("first_appearance"),
                hidden_note=serializer.validated_data.get("hidden_note", ""),
                initial_content=serializer.validated_data.get("initial_content"),
            )
        except PermissionError:
            return Response(
                {"success": False, "message": "권한이 없습니다.", "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = WikiEntryDetailSerializer(wiki)
        return Response(
            {"success": True, "message": "위키 생성 완료", "data": response_serializer.data},
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    retrieve=extend_schema(
        summary="위키 상세 조회",
        description="위키 엔트리 상세 정보를 조회합니다. ?chapter=N으로 문맥 인식 조회 가능.",
        tags=["Wiki"],
    ),
    partial_update=extend_schema(
        summary="위키 수정",
        description="위키 엔트리를 수정합니다.",
        tags=["Wiki"],
    ),
    destroy=extend_schema(
        summary="위키 삭제",
        description="위키 엔트리를 삭제합니다.",
        tags=["Wiki"],
    ),
)
class WikiEntryDetailViewSet(viewsets.ViewSet):
    """
    ViewSet for wiki operations by ID.

    Routes:
    - GET /wikis/{id}/ - Get wiki detail (with optional ?chapter=N)
    - PATCH /wikis/{id}/ - Update wiki
    - DELETE /wikis/{id}/ - Delete wiki
    - PUT /wikis/{id}/tags/ - Update wiki tags
    """

    def get_permissions(self):
        if self.action in ["retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, pk=None):
        """Get wiki detail, optionally with context-aware snapshot."""
        chapter = request.query_params.get("chapter")
        chapter = int(chapter) if chapter else None

        try:
            wiki = WikiService.retrieve(wiki_id=pk)
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WikiEntryDetailSerializer(wiki, context={"chapter": chapter})
        return Response({"success": True, "data": serializer.data})

    def partial_update(self, request, pk=None):
        """Update a wiki entry."""
        serializer = WikiEntryUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "유효성 검사 실패", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            wiki = WikiService.update(
                wiki_id=pk,
                user=request.user,
                **serializer.validated_data,
            )
        except PermissionError:
            return Response(
                {"success": False, "message": "권한이 없습니다.", "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = WikiEntryDetailSerializer(wiki)
        return Response({"success": True, "data": response_serializer.data})

    def destroy(self, request, pk=None):
        """Delete a wiki entry."""
        try:
            WikiService.delete(wiki_id=pk, user=request.user)
        except PermissionError:
            return Response(
                {"success": False, "message": "권한이 없습니다.", "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="위키 태그 업데이트",
        description="위키의 태그를 설정합니다.",
        tags=["Wiki"],
    )
    @action(detail=True, methods=["put"])
    def tags(self, request, pk=None):
        """Update wiki tags."""
        serializer = WikiTagUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "유효성 검사 실패", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            wiki = WikiService.update_tags(
                wiki_id=pk,
                user=request.user,
                tag_ids=serializer.validated_data["tag_ids"],
            )
        except PermissionError:
            return Response(
                {"success": False, "message": "권한이 없습니다.", "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = WikiEntryDetailSerializer(wiki)
        return Response({"success": True, "data": response_serializer.data})


@extend_schema_view(
    list=extend_schema(
        summary="태그 목록 조회",
        description="브랜치의 위키 태그 목록을 조회합니다.",
        tags=["Wiki"],
    ),
    create=extend_schema(
        summary="태그 생성",
        description="새 위키 태그를 생성합니다.",
        tags=["Wiki"],
    ),
)
class WikiTagViewSet(viewsets.ViewSet):
    """
    ViewSet for wiki tag definitions nested under branches.

    Routes:
    - GET /branches/{branch_id}/wiki-tags/ - List tags
    - POST /branches/{branch_id}/wiki-tags/ - Create tag
    """

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request, branch_pk=None):
        """List tag definitions for a branch."""
        tags = WikiService.list_tags(branch_id=branch_pk)
        serializer = WikiTagDefinitionSerializer(tags, many=True)
        return Response({"success": True, "data": serializer.data})

    def create(self, request, branch_pk=None):
        """Create a new tag definition."""
        serializer = WikiTagDefinitionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "유효성 검사 실패", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            tag = WikiService.create_tag(
                branch_id=branch_pk,
                user=request.user,
                **serializer.validated_data,
            )
        except PermissionError:
            return Response(
                {"success": False, "message": "권한이 없습니다.", "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = WikiTagDefinitionSerializer(tag)
        return Response(
            {"success": True, "data": response_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class WikiTagDetailViewSet(viewsets.ViewSet):
    """
    ViewSet for wiki tag operations by ID.

    Routes:
    - DELETE /wiki-tags/{id}/ - Delete tag
    """

    permission_classes = [IsAuthenticated]

    def destroy(self, request, pk=None):
        """Delete a tag definition."""
        try:
            WikiService.delete_tag(tag_id=pk, user=request.user)
        except PermissionError:
            return Response(
                {"success": False, "message": "권한이 없습니다.", "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(
        summary="스냅샷 목록 조회",
        description="위키의 스냅샷 목록을 조회합니다.",
        tags=["Wiki"],
    ),
    create=extend_schema(
        summary="스냅샷 생성",
        description="새 위키 스냅샷을 생성합니다.",
        tags=["Wiki"],
    ),
)
class WikiSnapshotViewSet(viewsets.ViewSet):
    """
    ViewSet for wiki snapshots nested under wikis.

    Routes:
    - GET /wikis/{wiki_id}/snapshots/ - List snapshots
    - POST /wikis/{wiki_id}/snapshots/ - Create snapshot
    """

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request, wiki_pk=None):
        """List snapshots for a wiki."""
        try:
            wiki = WikiService.retrieve(wiki_id=wiki_pk)
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WikiSnapshotSerializer(wiki.snapshots.all(), many=True)
        return Response({"success": True, "data": serializer.data})

    def create(self, request, wiki_pk=None):
        """Create a new snapshot."""
        serializer = WikiSnapshotCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "유효성 검사 실패", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            snapshot = WikiService.add_snapshot(
                wiki_id=wiki_pk,
                user=request.user,
                content=serializer.validated_data["content"],
                valid_from_chapter=serializer.validated_data["valid_from_chapter"],
            )
        except PermissionError:
            return Response(
                {"success": False, "message": "권한이 없습니다.", "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = WikiSnapshotSerializer(snapshot)
        return Response(
            {"success": True, "data": response_serializer.data},
            status=status.HTTP_201_CREATED,
        )
