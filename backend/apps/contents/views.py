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

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contents.map_services import MapService
from apps.contents.models import (
    Chapter,
    ChapterStatus,
    MapLayer,
    MapSnapshot,
)
from apps.contents.serializers import (
    ChapterCreateSerializer,
    ChapterDetailSerializer,
    ChapterListSerializer,
    ChapterScheduleSerializer,
    ChapterUpdateSerializer,
    MapCreateSerializer,
    MapDetailSerializer,
    MapLayerCreateSerializer,
    MapLayerSerializer,
    MapListSerializer,
    MapObjectCreateSerializer,
    MapObjectSerializer,
    MapSnapshotCreateSerializer,
    MapSnapshotSerializer,
    MapUpdateSerializer,
    WikiEntryCreateSerializer,
    WikiEntryDetailSerializer,
    WikiEntryListSerializer,
    WikiEntryUpdateSerializer,
    WikiSnapshotCreateSerializer,
    WikiSnapshotSerializer,
    WikiTagDefinitionCreateSerializer,
    WikiTagDefinitionSerializer,
    WikiTagUpdateSerializer,
)
from apps.contents.services import ChapterService, WikiService
from apps.novels.models import Branch
from apps.novels.services.draft_service import DraftService
from common.pagination import StandardPagination


class IsBranchAuthor:
    """Permission check for branch author."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request: Request, view: APIView, obj: Chapter) -> bool:
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

    def get_permissions(self) -> list:
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request: Request, branch_pk: int | None = None) -> Response:
        """
        List chapters for a branch, returning a paginated list visible to the requester.
        
        If the requester is the branch author, unpublished chapters (drafts) are included; otherwise only published chapters are returned.
        
        Parameters:
            request (Request): The incoming HTTP request; used to determine authentication and user.
            branch_pk (int | None): Primary key of the branch. If `None` or not found, a `NotFound` error is raised.
        
        Returns:
            Response: Paginated response containing serialized chapter list data.
        
        Raises:
            NotFound: If `branch_pk` is `None` or no branch with the given id exists.
        """
        if branch_pk is None:
            raise NotFound("브랜치를 찾을 수 없습니다.")

        service = ChapterService()

        # Check if user is branch author (can see drafts)
        try:
            branch = Branch.objects.get(pk=branch_pk)
        except Branch.DoesNotExist:
            raise NotFound("브랜치를 찾을 수 없습니다.")

        is_author = request.user.is_authenticated and branch.author == request.user
        chapters = service.list(branch_id=branch_pk, published_only=not is_author)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(chapters, request)
        serializer = ChapterListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def retrieve(
        self, request: Request, branch_pk: int | None = None, pk: int | None = None
    ) -> Response:
        """
        Retrieve chapter details for a given chapter number within a branch.
        
        Fetches the chapter identified by branch_pk and chapter number pk and returns its serialized detail. Unpublished chapters are accessible only to the branch author; other users will receive a not-found response.
        
        Parameters:
            request (Request): The incoming HTTP request (used to check user authentication).
            branch_pk (int | None): ID of the branch containing the chapter.
            pk (int | None): Chapter number within the branch.
        
        Returns:
            Response: Serialized chapter detail data.
        
        Raises:
            NotFound: If branch_pk is None, the branch does not exist, the chapter is not found, or the requester is not permitted to view an unpublished chapter.
            ValidationError: If pk is missing or cannot be parsed as an integer.
        """
        if branch_pk is None:
            raise NotFound("브랜치를 찾을 수 없습니다.")

        service = ChapterService()

        if pk is None:
            raise ValidationError("잘못된 회차 번호입니다.")

        try:
            chapter_number = int(pk)
        except (ValueError, TypeError):
            raise ValidationError("잘못된 회차 번호입니다.")

        chapter = service.retrieve(branch_id=branch_pk, chapter_number=chapter_number)

        if not chapter:
            raise NotFound("회차를 찾을 수 없습니다.")

        # Check access permissions
        if chapter.status != ChapterStatus.PUBLISHED:
            if not request.user.is_authenticated or chapter.branch.author != request.user:
                raise NotFound("회차를 찾을 수 없습니다.")

        serializer = ChapterDetailSerializer(chapter)
        return Response(serializer.data)

    def create(self, request: Request, branch_pk: int | None = None) -> Response:
        """
        Create a new chapter for the specified branch.
        
        Parameters:
            branch_pk (int | None): Primary key of the branch to create the chapter under; returns 404 if not found.
        
        Returns:
            Response: Serialized chapter detail data with HTTP 201 Created status.
        
        Raises:
            NotFound: If the branch does not exist.
            PermissionDenied: If the requesting user is not the branch author.
            ValidationError: If request data fails serializer validation.
        """
        # Get branch and verify ownership
        try:
            branch = Branch.objects.get(pk=branch_pk)
        except Branch.DoesNotExist:
            raise NotFound("브랜치를 찾을 수 없습니다.")

        if branch.author != request.user:
            raise PermissionDenied("권한이 없습니다.")

        serializer = ChapterCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

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

    @extend_schema(
        summary="초안 자동 저장",
        description="회차 초안을 Redis에 임시 저장합니다.",
        tags=["Chapters"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "title": {"type": "string"},
                    "chapter_id": {"type": "integer", "nullable": True},
                },
                "required": ["content"],
            }
        },
        responses={200: {"type": "object", "properties": {"success": {"type": "boolean"}}}},
    )
    @action(detail=False, methods=["post"], url_path="draft")
    def draft(self, request: Request, branch_pk: int | None = None) -> Response:
        """
        Auto-saves a draft for a chapter in the specified branch.
        
        Validates that the branch exists and the requester is the branch author, requires non-empty `content`, and persists the draft via the DraftService.
        
        Parameters:
            branch_pk (int | None): ID of the branch to which the draft belongs.
        
        Returns:
            Response: A response containing `{"success": True}` on success.
        
        Raises:
            NotFound: If `branch_pk` is None or the branch does not exist.
            PermissionDenied: If the requesting user is not the branch author.
            ValidationError: If `content` is missing or empty.
        """
        if branch_pk is None:
            raise NotFound("브랜치를 찾을 수 없습니다.")

        # Check if user is branch author
        try:
            branch = Branch.objects.get(pk=branch_pk)
        except Branch.DoesNotExist:
            raise NotFound("브랜치를 찾을 수 없습니다.")

        if branch.author != request.user:
            raise PermissionDenied("권한이 없습니다.")

        # Validation
        content = request.data.get("content")
        if content is None or (isinstance(content, str) and not content.strip()):
            raise ValidationError("내용은 필수입니다.")

        title = request.data.get("title", "")
        chapter_id = request.data.get("chapter_id")

        DraftService().save_draft(
            branch_id=int(branch_pk),
            chapter_id=chapter_id,
            title=title,
            content=content,
        )

        return Response({"success": True}, status=status.HTTP_200_OK)


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

    def get_permissions(self) -> list:
        if self.action in ["retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def _get_chapter(self, pk: int | None) -> Chapter | None:
        """Helper to get chapter by ID."""
        try:
            return Chapter.objects.select_related("branch").get(pk=pk)
        except Chapter.DoesNotExist:
            return None

    def _check_author(self, chapter: Chapter, user: object) -> bool:
        """Check if user is the branch author."""
        return chapter.branch.author == user

    def retrieve(self, request: Request, pk: int | None = None) -> Response:
        """Get chapter by ID."""
        chapter = self._get_chapter(pk)
        if not chapter:
            raise NotFound("회차를 찾을 수 없습니다.")

        serializer = ChapterDetailSerializer(chapter)
        return Response(serializer.data)

    def partial_update(self, request: Request, pk: int | None = None) -> Response:
        """Update a chapter."""
        chapter = self._get_chapter(pk)
        if not chapter:
            raise NotFound("회차를 찾을 수 없습니다.")

        if not self._check_author(chapter, request.user):
            raise PermissionDenied("권한이 없습니다.")

        serializer = ChapterUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        service = ChapterService()
        try:
            updated = service.update(chapter=chapter, **serializer.validated_data)
        except ValueError as e:
            raise ValidationError(str(e))

        response_serializer = ChapterDetailSerializer(updated)
        return Response(response_serializer.data)

    def destroy(self, request: Request, pk: int | None = None) -> Response:
        """Delete a chapter."""
        chapter = self._get_chapter(pk)
        if not chapter:
            raise NotFound("회차를 찾을 수 없습니다.")

        if not self._check_author(chapter, request.user):
            raise PermissionDenied("권한이 없습니다.")

        chapter.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="회차 발행",
        description="임시저장 회차를 즉시 발행합니다.",
        tags=["Chapters"],
    )
    @action(detail=True, methods=["post"])
    def publish(self, request: Request, pk: int | None = None) -> Response:
        """Publish a draft chapter."""
        chapter = self._get_chapter(pk)
        if not chapter:
            raise NotFound("회차를 찾을 수 없습니다.")

        if not self._check_author(chapter, request.user):
            raise PermissionDenied("권한이 없습니다.")

        service = ChapterService()
        try:
            published = service.publish(chapter=chapter)
        except ValueError as e:
            raise ValidationError(str(e))

        serializer = ChapterDetailSerializer(published)
        return Response(serializer.data)

    @extend_schema(
        summary="회차 예약 발행",
        description="회차를 예약 발행 설정합니다.",
        tags=["Chapters"],
    )
    @action(detail=True, methods=["post"])
    def schedule(self, request: Request, pk: int | None = None) -> Response:
        """Schedule a chapter for future publication."""
        chapter = self._get_chapter(pk)
        if not chapter:
            raise NotFound("회차를 찾을 수 없습니다.")

        if not self._check_author(chapter, request.user):
            raise PermissionDenied("권한이 없습니다.")

        serializer = ChapterScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ChapterService()
        try:
            scheduled = service.schedule(
                chapter=chapter,
                scheduled_at=serializer.validated_data["scheduled_at"],
            )
        except ValueError as e:
            raise ValidationError(str(e))

        response_serializer = ChapterDetailSerializer(scheduled)
        return Response(response_serializer.data)

    @extend_schema(
        summary="북마크 추가/삭제",
        description="회차에 북마크를 추가하거나 삭제합니다.",
        tags=["Reading"],
    )
    @action(detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated])
    def bookmark(self, request: Request, pk: int | None = None) -> Response:
        """
        Handle adding or removing a bookmark for the specified chapter.
        
        On POST, validates input and creates a bookmark for the requesting user. On DELETE, removes the user's bookmark for the chapter.
        
        Returns:
            Serialized bookmark data with HTTP 201 on successful create; empty response with HTTP 204 on successful delete.
        
        Raises:
            NotFound: If the chapter identified by `pk` does not exist.
        """
        from apps.interactions.serializers import BookmarkCreateSerializer, BookmarkSerializer
        from apps.interactions.services import BookmarkService

        chapter = self._get_chapter(pk)
        if not chapter:
            raise NotFound("회차를 찾을 수 없습니다.")

        # pk is validated by _get_chapter returning a valid chapter
        chapter_id = chapter.id

        if request.method == "POST":
            serializer = BookmarkCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            bookmark = BookmarkService.add_bookmark(
                user=request.user,
                chapter_id=chapter_id,
                scroll_position=serializer.validated_data.get("scroll_position", 0),
                note=serializer.validated_data.get("note", ""),
            )
            return Response(BookmarkSerializer(bookmark).data, status=status.HTTP_201_CREATED)
        else:  # DELETE
            BookmarkService.remove_bookmark(user=request.user, chapter_id=chapter_id)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="읽은 기록 저장",
        description="회차 읽은 진행률을 저장합니다.",
        tags=["Reading"],
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="reading-progress",
        permission_classes=[IsAuthenticated],
    )
    def reading_progress(self, request: Request, pk: int | None = None) -> Response:
        """
        Record and return a reading progress log for the specified chapter.
        
        Returns:
            reading_log (dict): Serialized reading log data for the recorded progress.
        
        Raises:
            NotFound: If the chapter identified by `pk` does not exist.
        """
        from apps.interactions.serializers import ReadingLogSerializer, ReadingProgressSerializer
        from apps.interactions.services import ReadingService

        chapter = self._get_chapter(pk)
        if not chapter:
            raise NotFound("회차를 찾을 수 없습니다.")

        serializer = ReadingProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        log = ReadingService.record_reading(
            user=request.user,
            chapter_id=chapter.id,
            progress=float(serializer.validated_data["progress"]),
        )
        return Response(ReadingLogSerializer(log).data)


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

    def get_permissions(self) -> list:
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request: Request, branch_pk: int | None = None) -> Response:
        """
        List wiki entries for the specified branch.
        
        Accepts optional query parameters `tag` (tag id) and `currentChapter` (chapter number) to filter results. Raises `NotFound` when `branch_pk` is None.
        
        Parameters:
            branch_pk (int | None): ID of the branch to list wikis for.
        
        Returns:
            Response: Paginated response containing serialized wiki entry list.
        """
        if branch_pk is None:
            raise NotFound("브랜치를 찾을 수 없습니다.")

        tag_id = request.query_params.get("tag")
        tag_id = int(tag_id) if tag_id else None

        current_chapter = request.query_params.get("currentChapter")
        current_chapter = int(current_chapter) if current_chapter else None

        wikis = WikiService.list(
            branch_id=branch_pk, tag_id=tag_id, current_chapter=current_chapter
        )

        paginator = StandardPagination()
        page = paginator.paginate_queryset(wikis, request)
        serializer = WikiEntryListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def create(self, request: Request, branch_pk: int | None = None) -> Response:
        """
        Create a wiki entry under the specified branch.
        
        Parameters:
            branch_pk (int | None): ID of the branch to create the wiki entry under.
        
        Returns:
            dict: Serialized detail representation of the created wiki entry.
        
        Raises:
            NotFound: If `branch_pk` is None or the branch cannot be found.
            PermissionDenied: If the user is not allowed to create a wiki entry on the branch.
            ValidationError: If input validation fails or the service reports a validation error.
        """
        if branch_pk is None:
            raise NotFound("브랜치를 찾을 수 없습니다.")

        serializer = WikiEntryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

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
            raise PermissionDenied("권한이 없습니다.")
        except ValueError as e:
            raise ValidationError(str(e))

        response_serializer = WikiEntryDetailSerializer(wiki)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


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

    def get_permissions(self) -> list:
        if self.action in ["retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request: Request, pk: int | None = None) -> Response:
        """
        Retrieve a wiki entry's detail, optionally scoped to a chapter for context.
        
        The endpoint accepts an optional `chapter` query parameter (integer) to include chapter-aware snapshot/context in the returned representation.
        
        Parameters:
            pk (int | None): ID of the wiki entry to retrieve.
        
        Returns:
            dict: Serialized wiki detail data, possibly including chapter-scoped context when `chapter` is provided.
        
        Raises:
            NotFound: If `pk` is None or the wiki entry does not exist.
        """
        if pk is None:
            raise NotFound("위키를 찾을 수 없습니다.")

        chapter = request.query_params.get("chapter")
        chapter = int(chapter) if chapter else None

        try:
            wiki = WikiService.retrieve(wiki_id=pk)
        except ValueError as e:
            raise NotFound(str(e))

        serializer = WikiEntryDetailSerializer(wiki, context={"chapter": chapter})
        return Response(serializer.data)

    def partial_update(self, request: Request, pk: int | None = None) -> Response:
        """
        Partially update a wiki entry identified by its ID.
        
        Returns:
            dict: Serialized wiki detail representation.
        
        Raises:
            NotFound: If `pk` is None or the wiki does not exist.
            PermissionDenied: If the requesting user is not allowed to update the wiki.
            ValidationError: If input data is invalid or service-level validation fails.
        """
        if pk is None:
            raise NotFound("위키를 찾을 수 없습니다.")

        serializer = WikiEntryUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            wiki = WikiService.update(
                wiki_id=pk,
                user=request.user,
                **serializer.validated_data,
            )
        except PermissionError:
            raise PermissionDenied("권한이 없습니다.")
        except ValueError as e:
            raise ValidationError(str(e))

        response_serializer = WikiEntryDetailSerializer(wiki)
        return Response(response_serializer.data)

    def destroy(self, request: Request, pk: int | None = None) -> Response:
        """
        Delete the specified wiki entry.
        
        Parameters:
            pk: ID of the wiki to delete. If None, a NotFound error is raised.
        
        Returns:
            Response: HTTP 204 No Content on successful deletion.
        
        Raises:
            NotFound: If `pk` is None or the wiki does not exist.
            PermissionDenied: If the requesting user is not authorized to delete the wiki.
        """
        if pk is None:
            raise NotFound("위키를 찾을 수 없습니다.")

        try:
            WikiService.delete(wiki_id=pk, user=request.user)
        except PermissionError:
            raise PermissionDenied("권한이 없습니다.")
        except ValueError as e:
            raise NotFound(str(e))

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="위키 태그 업데이트",
        description="위키의 태그를 설정합니다.",
        tags=["Wiki"],
    )
    @action(detail=True, methods=["put"])
    def tags(self, request: Request, pk: int | None = None) -> Response:
        """
        Update tags for a wiki entry.
        
        Parameters:
            pk (int | None): ID of the wiki to update.
        
        Returns:
            dict: Serialized wiki entry data as returned by WikiEntryDetailSerializer.
        
        Raises:
            NotFound: If `pk` is None or the wiki cannot be found.
            PermissionDenied: If the requesting user is not authorized to update tags.
            ValidationError: If input validation fails or the service raises a value error.
        """
        if pk is None:
            raise NotFound("위키를 찾을 수 없습니다.")

        serializer = WikiTagUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            wiki = WikiService.update_tags(
                wiki_id=pk,
                user=request.user,
                tag_ids=serializer.validated_data["tag_ids"],
            )
        except PermissionError:
            raise PermissionDenied("권한이 없습니다.")
        except ValueError as e:
            raise ValidationError(str(e))

        response_serializer = WikiEntryDetailSerializer(wiki)
        return Response(response_serializer.data)


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

    def get_permissions(self) -> list:
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request: Request, branch_pk: int | None = None) -> Response:
        """
        Retrieve wiki tag definitions for a branch.
        
        Parameters:
            branch_pk (int | None): ID of the branch whose wiki tag definitions will be listed.
        
        Returns:
            tags (list): Serialized wiki tag definition objects.
        
        Raises:
            NotFound: If `branch_pk` is None.
        """
        if branch_pk is None:
            raise NotFound("브랜치를 찾을 수 없습니다.")

        tags = WikiService.list_tags(branch_id=branch_pk)
        serializer = WikiTagDefinitionSerializer(tags, many=True)
        return Response(serializer.data)

    def create(self, request: Request, branch_pk: int | None = None) -> Response:
        """
        Create a new wiki tag definition for a specific branch.
        
        Parameters:
            request (Request): The incoming HTTP request containing tag data.
            branch_pk (int | None): ID of the branch the tag will belong to.
        
        Returns:
            dict: Serialized wiki tag definition returned in the response body with HTTP 201 status.
        
        Raises:
            NotFound: If `branch_pk` is None.
            PermissionDenied: If the user is not allowed to create a tag for the branch.
            ValidationError: If input validation fails or the service reports a value error.
        """
        if branch_pk is None:
            raise NotFound("브랜치를 찾을 수 없습니다.")

        serializer = WikiTagDefinitionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tag = WikiService.create_tag(
                branch_id=branch_pk,
                user=request.user,
                **serializer.validated_data,
            )
        except PermissionError:
            raise PermissionDenied("권한이 없습니다.")
        except ValueError as e:
            raise ValidationError(str(e))

        response_serializer = WikiTagDefinitionSerializer(tag)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class WikiTagDetailViewSet(viewsets.ViewSet):
    """
    ViewSet for wiki tag operations by ID.

    Routes:
    - DELETE /wiki-tags/{id}/ - Delete tag
    """

    permission_classes = [IsAuthenticated]

    def destroy(self, request: Request, pk: int | None = None) -> Response:
        """
        Delete a wiki tag definition identified by `pk`.
        
        Parameters:
            pk (int | None): ID of the tag to delete.
        
        Returns:
            Response: HTTP 204 No Content on successful deletion.
        
        Raises:
            NotFound: If `pk` is None or no tag exists with the given ID.
            PermissionDenied: If the requesting user is not authorized to delete the tag.
        """
        if pk is None:
            raise NotFound("태그를 찾을 수 없습니다.")

        try:
            WikiService.delete_tag(tag_id=pk, user=request.user)
        except PermissionError:
            raise PermissionDenied("권한이 없습니다.")
        except ValueError as e:
            raise NotFound(str(e))

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

    def get_permissions(self) -> list:
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request: Request, wiki_pk: int | None = None) -> Response:
        """
        List snapshot entries for a wiki.
        
        Parameters:
            wiki_pk (int | None): ID of the wiki whose snapshots should be listed.
        
        Returns:
            list: Serialized list of the wiki's snapshots.
        
        Raises:
            NotFound: If `wiki_pk` is None or if the wiki does not exist.
        """
        if wiki_pk is None:
            raise NotFound("위키를 찾을 수 없습니다.")

        try:
            wiki = WikiService.retrieve(wiki_id=wiki_pk)
        except ValueError as e:
            raise NotFound(str(e))

        serializer = WikiSnapshotSerializer(wiki.snapshots.all(), many=True)
        return Response(serializer.data)

    def create(self, request: Request, wiki_pk: int | None = None) -> Response:
        """
        Create a new wiki snapshot for the specified wiki.
        
        Parameters:
            wiki_pk (int | None): ID of the wiki to attach the snapshot to.
        
        Returns:
            response (Response): Serialized snapshot data with HTTP 201 Created.
        
        Raises:
            NotFound: If `wiki_pk` is None or the wiki cannot be found.
            PermissionDenied: If the requesting user is not authorized to add a snapshot.
            ValidationError: If input validation fails or the service raises a value error.
        """
        if wiki_pk is None:
            raise NotFound("위키를 찾을 수 없습니다.")

        serializer = WikiSnapshotCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            snapshot = WikiService.add_snapshot(
                wiki_id=wiki_pk,
                user=request.user,
                content=serializer.validated_data["content"],
                valid_from_chapter=serializer.validated_data["valid_from_chapter"],
            )
        except PermissionError:
            raise PermissionDenied("권한이 없습니다.")
        except ValueError as e:
            raise ValidationError(str(e))

        response_serializer = WikiSnapshotSerializer(snapshot)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# =============================================================================
# Map ViewSets
# =============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="지도 목록 조회",
        description="브랜치의 지도 목록을 조회합니다.",
        tags=["Maps"],
    ),
    create=extend_schema(
        summary="지도 생성",
        description="새 지도를 생성합니다.",
        tags=["Maps"],
    ),
)
class MapViewSet(viewsets.ViewSet):
    """
    ViewSet for maps nested under branches.

    Routes:
    - GET /branches/{branch_id}/maps/ - List maps
    - POST /branches/{branch_id}/maps/ - Create map
    """

    pagination_class = StandardPagination

    def get_permissions(self) -> list:
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request: Request, branch_pk: int | None = None) -> Response:
        """
        List maps belonging to the specified branch.
        
        Retrieves maps for the branch identified by `branch_pk`, paginates the results, and returns serialized list data suitable for the list endpoint. Raises NotFound if `branch_pk` is None.
        
        Parameters:
            branch_pk (int | None): ID of the branch whose maps should be listed.
        
        Returns:
            Paginated serialized map list data for the given branch.
        """
        if branch_pk is None:
            raise NotFound("브랜치를 찾을 수 없습니다.")

        maps = MapService.list(branch_id=branch_pk)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(maps, request)
        serializer = MapListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def create(self, request: Request, branch_pk: int | None = None) -> Response:
        """
        Create a new map under the specified branch.
        
        Parameters:
            branch_pk (int | None): ID of the branch to create the map under.
        
        Returns:
            dict: Serialized map detail data.
        
        Raises:
            NotFound: If `branch_pk` is None or the branch does not exist.
            PermissionDenied: If the requesting user is not allowed to create a map in the branch.
            ValidationError: If input data is invalid.
        """
        if branch_pk is None:
            raise NotFound("브랜치를 찾을 수 없습니다.")

        serializer = MapCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            map_obj = MapService.create(
                branch_id=branch_pk,
                user=request.user,
                **serializer.validated_data,
            )
        except PermissionError:
            raise PermissionDenied("권한이 없습니다.")
        except ValueError as e:
            raise ValidationError(str(e))

        response_serializer = MapDetailSerializer(map_obj)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    retrieve=extend_schema(
        summary="지도 상세 조회",
        description="지도 상세 정보를 조회합니다. ?currentChapter=N으로 문맥 인식 조회 가능.",
        tags=["Maps"],
    ),
    partial_update=extend_schema(
        summary="지도 수정",
        description="지도를 수정합니다.",
        tags=["Maps"],
    ),
    destroy=extend_schema(
        summary="지도 삭제",
        description="지도를 삭제합니다.",
        tags=["Maps"],
    ),
)
class MapDetailViewSet(viewsets.ViewSet):
    """
    ViewSet for map operations by ID.

    Routes:
    - GET /maps/{id}/ - Get map detail (with optional ?currentChapter=N)
    - PATCH /maps/{id}/ - Update map
    - DELETE /maps/{id}/ - Delete map
    """

    def get_permissions(self) -> list:
        if self.action in ["retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request: Request, pk: int | None = None) -> Response:
        """
        Retrieve detailed map information, optionally scoped to a specific chapter.
        
        Accepts an optional query parameter `currentChapter` (integer) to provide chapter-aware context for the serialized map. Raises NotFound if `pk` is None or the map cannot be located.
        
        Parameters:
            pk (int | None): ID of the map to retrieve.
        
        Returns:
            dict: Serialized data from MapDetailSerializer, using `chapter` in context when `currentChapter` is provided.
        
        Raises:
            NotFound: If `pk` is None or MapService.retrieve raises a ValueError indicating the map was not found.
        """
        if pk is None:
            raise NotFound("지도를 찾을 수 없습니다.")

        chapter = request.query_params.get("currentChapter")
        chapter = int(chapter) if chapter else None

        try:
            map_obj = MapService.retrieve(map_id=pk)
        except ValueError as e:
            raise NotFound(str(e))

        serializer = MapDetailSerializer(map_obj, context={"chapter": chapter})
        return Response(serializer.data)

    def partial_update(self, request: Request, pk: int | None = None) -> Response:
        """
        Partially update a map identified by its ID.
        
        Parameters:
            pk (int | None): ID of the map to update.
        
        Returns:
            Response: Serialized updated map using MapDetailSerializer.
        
        Raises:
            NotFound: If `pk` is None or the map does not exist.
            PermissionDenied: If the requesting user is not authorized to update the map.
            ValidationError: If provided data fails validation or update constraints.
        """
        if pk is None:
            raise NotFound("지도를 찾을 수 없습니다.")

        serializer = MapUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            map_obj = MapService.update(
                map_id=pk,
                user=request.user,
                **serializer.validated_data,
            )
        except PermissionError:
            raise PermissionDenied("권한이 없습니다.")
        except ValueError as e:
            raise ValidationError(str(e))

        response_serializer = MapDetailSerializer(map_obj)
        return Response(response_serializer.data)

    def destroy(self, request: Request, pk: int | None = None) -> Response:
        """
        Delete a map identified by its ID.
        
        Parameters:
            pk (int | None): ID of the map to delete.
        
        Returns:
            Response: HTTP 204 NO CONTENT on successful deletion.
        
        Raises:
            NotFound: If `pk` is None or no map with the given ID exists.
            PermissionDenied: If the requesting user is not authorized to delete the map.
        """
        if pk is None:
            raise NotFound("지도를 찾을 수 없습니다.")

        try:
            MapService.delete(map_id=pk, user=request.user)
        except PermissionError:
            raise PermissionDenied("권한이 없습니다.")
        except ValueError as e:
            raise NotFound(str(e))

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(
        summary="지도 스냅샷 목록 조회",
        description="지도의 스냅샷 목록을 조회합니다.",
        tags=["Maps"],
    ),
    create=extend_schema(
        summary="지도 스냅샷 생성",
        description="새 지도 스냅샷을 생성합니다.",
        tags=["Maps"],
    ),
)
class MapSnapshotViewSet(viewsets.ViewSet):
    """
    ViewSet for map snapshots nested under maps.

    Routes:
    - GET /maps/{map_id}/snapshots/ - List snapshots
    - POST /maps/{map_id}/snapshots/ - Create snapshot
    """

    def get_permissions(self) -> list:
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request: Request, map_pk: int | None = None) -> Response:
        """List snapshots for a map."""
        if map_pk is None:
            raise NotFound("지도를 찾을 수 없습니다.")

        try:
            map_obj = MapService.retrieve(map_id=map_pk)
        except ValueError as e:
            raise NotFound(str(e))

        serializer = MapSnapshotSerializer(map_obj.snapshots.all(), many=True)
        return Response(serializer.data)

    def create(self, request: Request, map_pk: int | None = None) -> Response:
        """
        Create a new snapshot for the specified map.
        
        Parameters:
            request (Request): The incoming HTTP request containing snapshot data.
            map_pk (int | None): ID of the map to add the snapshot to; required.
        
        Returns:
            Response: HTTP 201 response containing the created snapshot serialized by MapSnapshotSerializer.
        
        Raises:
            NotFound: If `map_pk` is None (map not found).
            PermissionDenied: If the user is not allowed to create a snapshot for the map.
            ValidationError: If the provided data is invalid or MapService reports a value error.
        """
        if map_pk is None:
            raise NotFound("지도를 찾을 수 없습니다.")

        serializer = MapSnapshotCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            snapshot = MapService.create_snapshot(
                map_id=map_pk,
                user=request.user,
                **serializer.validated_data,
            )
        except PermissionError:
            raise PermissionDenied("권한이 없습니다.")
        except ValueError as e:
            raise ValidationError(str(e))

        response_serializer = MapSnapshotSerializer(snapshot)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(
        summary="레이어 목록 조회",
        description="스냅샷의 레이어 목록을 조회합니다.",
        tags=["Maps"],
    ),
    create=extend_schema(
        summary="레이어 생성",
        description="새 레이어를 생성합니다.",
        tags=["Maps"],
    ),
)
class MapLayerViewSet(viewsets.ViewSet):
    """
    ViewSet for map layers nested under snapshots.

    Routes:
    - GET /snapshots/{snapshot_id}/layers/ - List layers
    - POST /snapshots/{snapshot_id}/layers/ - Create layer
    """

    def get_permissions(self) -> list:
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request: Request, snapshot_pk: int | None = None) -> Response:
        """
        List map layers for the specified snapshot.
        
        Parameters:
            snapshot_pk (int | None): ID of the MapSnapshot whose layers will be listed.
        
        Returns:
            Response: DRF Response containing a serialized list of map layers.
        
        Raises:
            NotFound: If no MapSnapshot exists with the given `snapshot_pk`.
        """
        try:
            snapshot = MapSnapshot.objects.prefetch_related("layers__map_objects").get(
                id=snapshot_pk
            )
        except MapSnapshot.DoesNotExist:
            raise NotFound("스냅샷을 찾을 수 없습니다.")

        serializer = MapLayerSerializer(snapshot.layers.all(), many=True)
        return Response(serializer.data)

    def create(self, request: Request, snapshot_pk: int | None = None) -> Response:
        """
        Create a new map layer under the given snapshot.
        
        Parameters:
            request (Request): The HTTP request containing layer data.
            snapshot_pk (int | None): ID of the parent snapshot; raises NotFound if None.
        
        Returns:
            response (dict): Serialized data of the created MapLayer.
        
        Raises:
            NotFound: If `snapshot_pk` is None.
            PermissionDenied: If the requesting user is not allowed to add a layer.
            ValidationError: If input validation fails or service returns a value error.
        """
        if snapshot_pk is None:
            raise NotFound("스냅샷을 찾을 수 없습니다.")

        serializer = MapLayerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            layer = MapService.add_layer(
                snapshot_id=snapshot_pk,
                user=request.user,
                **serializer.validated_data,
            )
        except PermissionError:
            raise PermissionDenied("권한이 없습니다.")
        except ValueError as e:
            raise ValidationError(str(e))

        response_serializer = MapLayerSerializer(layer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(
        summary="오브젝트 목록 조회",
        description="레이어의 오브젝트 목록을 조회합니다.",
        tags=["Maps"],
    ),
    create=extend_schema(
        summary="오브젝트 생성",
        description="새 오브젝트를 생성합니다.",
        tags=["Maps"],
    ),
)
class MapObjectViewSet(viewsets.ViewSet):
    """
    ViewSet for map objects nested under layers.

    Routes:
    - GET /layers/{layer_id}/objects/ - List objects
    - POST /layers/{layer_id}/objects/ - Create object
    """

    def get_permissions(self) -> list:
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request: Request, layer_pk: int | None = None) -> Response:
        """List objects for a layer."""
        try:
            layer = MapLayer.objects.prefetch_related("map_objects").get(id=layer_pk)
        except MapLayer.DoesNotExist:
            raise NotFound("레이어를 찾을 수 없습니다.")

        serializer = MapObjectSerializer(layer.map_objects.all(), many=True)
        return Response(serializer.data)

    def create(self, request: Request, layer_pk: int | None = None) -> Response:
        """
        Create a new map object within the specified map layer.
        
        Validates the provided layer identifier and input data, enforces authorisation, and returns the created object's serialized representation.
        
        Parameters:
            layer_pk (int | None): ID of the parent map layer.
        
        Returns:
            dict: Serialized map object data.
        """
        if layer_pk is None:
            raise NotFound("레이어를 찾을 수 없습니다.")

        serializer = MapObjectCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            obj = MapService.add_object(
                layer_id=layer_pk,
                user=request.user,
                **serializer.validated_data,
            )
        except PermissionError:
            raise PermissionDenied("권한이 없습니다.")
        except ValueError as e:
            raise ValidationError(str(e))

        response_serializer = MapObjectSerializer(obj)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)