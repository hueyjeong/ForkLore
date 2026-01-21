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
        지점(branch)의 챕터 목록을 페이지네이션된 응답으로 제공한다.
        
        작성자 본인인 경우에는 초안(draft)을 포함한 모든 챕터를, 아닌 경우에는 공개(published)된 챕터만 반환한다. branch_pk가 없거나 해당 지점이 존재하지 않으면 NotFound 예외를 발생시킨다.
        
        Parameters:
            branch_pk (int | None): 조회할 지점의 ID. None이거나 존재하지 않으면 NotFound가 발생한다.
        
        Returns:
            Response: 직렬화된 챕터 객체들의 페이지네이션된 응답.
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
        지정된 브랜치에서 주어진 회차 번호에 해당하는 챕터의 상세 직렬화 데이터를 반환합니다.
        
        Parameters:
            branch_pk (int | None): 조회할 챕터가 속한 브랜치의 ID. None이면 조회할 수 없음.
            pk (int | None): 조회할 회차 번호(정수로 변환 가능한 값).
        
        Returns:
            dict: 챕터 상세 직렬화 데이터.
        
        Raises:
            NotFound: branch_pk가 None이거나 해당 회차가 존재하지 않거나 접근 권한이 없어 조회할 수 없을 때.
            ValidationError: pk가 제공되지 않았거나 정수로 변환할 수 없을 때.
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
        지정된 브랜치에 새 챕터를 생성한다.
        
        Parameters:
            branch_pk (int | None): 챕터를 생성할 브랜치의 식별자.
        
        Returns:
            dict: 생성된 챕터의 직렬화된 데이터.
        
        Raises:
            NotFound: 지정한 브랜치를 찾을 수 없을 때.
            PermissionDenied: 요청 사용자가 브랜치의 작성자가 아닐 때.
            ValidationError: 요청 데이터가 유효하지 않을 때.
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
        챕터의 임시 초안(드래프트)을 검증 후 저장한다.
        
        Parameters:
            request (Request): 요청 객체로, 저장할 드래프트의 데이터(`content`, 선택적 `title`, 선택적 `chapter_id`)와 요청자 정보를 포함한다.
            branch_pk (int | None): 드래프트를 저장할 대상 브랜치의 ID.
        
        Returns:
            response (dict): {"success": True} — 드래프트가 성공적으로 저장되었음을 나타낸다.
        
        Raises:
            NotFound: branch_pk가 누락되었거나 해당 브랜치가 존재하지 않을 때 발생한다.
            PermissionDenied: 요청 사용자가 브랜치 작성자가 아닐 때 발생한다.
            ValidationError: content가 비어있거나 chapter_id가 유효한 정수가 아닐 때 발생한다.
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
        if content is None or not isinstance(content, str) or not content.strip():
            raise ValidationError("내용은 필수입니다.")

        title = request.data.get("title", "")
        chapter_id = request.data.get("chapter_id")
        if chapter_id is not None:
            try:
                chapter_id = int(chapter_id)
            except (ValueError, TypeError):
                raise ValidationError("유효하지 않은 회차 ID입니다.")

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
        회차에 대해 북마크를 추가하거나 제거합니다.
        
        Parameters:
            request (Request): 요청 객체. POST일 경우 북마크 생성 데이터를 포함해야 합니다.
            pk (int | None): 대상 회차의 기본 키.
        
        Returns:
            dict: POST일 때 생성된 북마크의 직렬화된 데이터.
            None: DELETE일 때 반환 내용이 없으며 상태 코드 204를 사용합니다.
        
        Raises:
            NotFound: 지정한 회차를 찾을 수 없는 경우 발생합니다.
        """
        from apps.interactions.serializers import BookmarkCreateSerializer, BookmarkSerializer
        from apps.interactions.services import BookmarkService

        # Use simple get without select_related - bookmark doesn't need branch
        try:
            chapter = Chapter.objects.get(pk=pk)
        except Chapter.DoesNotExist:
            raise NotFound("회차를 찾을 수 없습니다.")

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
        요청 사용자의 챕터 읽기 진행률을 기록합니다.
        
        요청 바디의 진행률 데이터를 검증한 뒤 ReadingService에 기록하고, 생성되거나 갱신된 읽기 로그의 직렬화된 데이터를 반환합니다.
        
        Parameters:
        	request (Request): 요청 객체.
        	pk (int | None): 대상 챕터의 기본 키(ID).
        
        Returns:
        	reading_log (dict): 생성되거나 갱신된 읽기 로그의 직렬화된 표현.
        
        Raises:
        	NotFound: 지정한 챕터를 찾을 수 없을 경우 발생합니다.
        	ValidationError: 전송된 진행률 데이터가 유효하지 않을 경우 발생합니다.
        """
        from apps.interactions.serializers import ReadingLogSerializer, ReadingProgressSerializer
        from apps.interactions.services import ReadingService

        # Use simple get without select_related - reading progress doesn't need branch
        try:
            chapter = Chapter.objects.get(pk=pk)
        except Chapter.DoesNotExist:
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
        브랜치에 속한 위키 항목을 조회하여 페이지별 직렬화된 목록을 반환합니다.
        
        쿼리 파라미터:
        - tag: 태그 ID로 필터링(정수).
        - currentChapter: 컨텍스트가 될 챕터 번호(정수).
        
        Parameters:
            request (Request): HTTP 요청 객체(쿼리 파라미터 'tag' 및 'currentChapter' 사용).
            branch_pk (int | None): 대상 브랜치의 ID. None이면 NotFound가 발생합니다.
        
        Returns:
            Response: 페이지네이션된 위키 항목 직렬화 결과를 포함하는 DRF 응답 객체.
        
        Raises:
            NotFound: branch_pk가 제공되지 않았거나 브랜치를 찾을 수 없을 때.
            ValidationError: currentChapter 쿼리 파라미터가 숫자가 아닐 때.
        """
        if branch_pk is None:
            raise NotFound("브랜치를 찾을 수 없습니다.")

        tag_id = request.query_params.get("tag")
        tag_id = int(tag_id) if tag_id else None

        current_chapter = request.query_params.get("currentChapter")
        if current_chapter:
            try:
                current_chapter = int(current_chapter)
            except (ValueError, TypeError):
                raise ValidationError("currentChapter must be a number")
        else:
            current_chapter = None

        wikis = WikiService.list(
            branch_id=branch_pk, tag_id=tag_id, current_chapter=current_chapter
        )

        paginator = StandardPagination()
        page = paginator.paginate_queryset(wikis, request)
        serializer = WikiEntryListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def create(self, request: Request, branch_pk: int | None = None) -> Response:
        """
        새 위키 항목을 생성한다.
        
        Parameters:
            request (Request): 클라이언트 요청 객체 (생성할 위키 데이터 포함).
            branch_pk (int | None): 위키를 생성할 브랜치의 ID. None인 경우 예외가 발생한다.
        
        Returns:
            dict: 생성된 위키 항목의 상세를 직렬화한 데이터.
        
        Raises:
            NotFound: branch_pk가 없거나 해당 브랜치를 찾을 수 없을 때 발생.
            PermissionDenied: 사용자가 해당 브랜치에 위키를 생성할 권한이 없을 때 발생.
            ValidationError: 입력 데이터가 유효하지 않거나 서비스 레이어에서 유효성 오류가 발생할 때 발생.
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
        위키의 상세 정보를 반환하며, 쿼리 매개변수 `chapter`가 제공되면 해당 챕터 컨텍스트에 맞는 스냅샷을 포함합니다.
        
        Parameters:
        	pk (int | None): 조회할 위키의 ID.
        
        Returns:
        	직렬화된 위키 상세 데이터. `chapter` 쿼리 매개변수가 있으면 그 챕터를 기준으로 한 스냅샷을 포함합니다.
        
        Raises:
        	NotFound: `pk`가 제공되지 않았거나 해당 위키를 찾을 수 없는 경우.
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
        위키 항목의 일부 필드를 업데이트합니다.
        
        Parameters:
            request (Request): 수정할 필드를 포함한 요청 객체.
            pk (int | None): 수정 대상 위키의 ID.
        
        Returns:
            dict: 업데이트된 위키 항목의 직렬화된 상세 데이터.
        
        Raises:
            NotFound: pk가 주어지지 않았거나 해당 위키를 찾을 수 없을 때 발생합니다.
            PermissionDenied: 요청 사용자가 수정 권한이 없을 때 발생합니다.
            ValidationError: 요청 데이터가 유효하지 않거나 서비스 수준 검증에서 실패할 때 발생합니다.
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
        위키 항목을 삭제합니다.
        
        지정한 `pk`에 해당하는 위키를 삭제하고 성공하면 204 No Content 응답을 반환합니다.
        
        Parameters:
            request (Request): 요청 객체(삭제 권한 검증에 사용).
            pk (int | None): 삭제할 위키의 ID. 제공되지 않으면 NotFound를 발생시킵니다.
        
        Returns:
            Response: 삭제 성공 시 204 No Content 응답.
        
        Raises:
            NotFound: `pk`가 없거나 해당 위키를 찾을 수 없을 때 발생합니다.
            PermissionDenied: 요청 사용자가 삭제 권한이 없을 때 발생합니다.
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
        위키의 태그 목록을 갱신한다.
        
        Parameters:
            pk (int | None): 태그를 갱신할 대상 위키의 ID. None이면 NotFound가 발생한다.
            request.data (dict): `{"tag_ids": [int, ...]}` 형태의 태그 ID 리스트를 포함해야 한다.
        
        Returns:
            dict: 갱신된 위키의 상세 정보를 직렬화한 데이터.
        
        Raises:
            NotFound: pk가 None이거나 대상 위키를 찾을 수 없을 때.
            PermissionDenied: 요청 사용자가 태그 갱신 권한이 없을 때.
            ValidationError: 입력 데이터가 유효하지 않거나 서비스 레벨 검증에 실패했을 때.
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
        브랜치에 정의된 위키 태그 정의들의 직렬화된 목록을 반환합니다.
        
        Parameters:
            branch_pk (int | None): 조회 대상 브랜치의 식별자.
        
        Raises:
            NotFound: branch_pk가 제공되지 않을 경우 발생합니다.
        
        Returns:
            list: 직렬화된 위키 태그 정의 객체들의 리스트 데이터.
        """
        if branch_pk is None:
            raise NotFound("브랜치를 찾을 수 없습니다.")

        tags = WikiService.list_tags(branch_id=branch_pk)
        serializer = WikiTagDefinitionSerializer(tags, many=True)
        return Response(serializer.data)

    def create(self, request: Request, branch_pk: int | None = None) -> Response:
        """
        브랜치에 새 위키 태그 정의를 생성합니다.
        
        Parameters:
            branch_pk (int | None): 태그를 생성할 대상 브랜치의 ID. None이면 NotFound가 발생합니다.
        
        Returns:
            Response: 생성된 태그 정의의 직렬화된 데이터가 담긴 응답(HTTP 201).
        
        Raises:
            NotFound: branch_pk가 None이거나 브랜치를 찾을 수 없는 경우.
            PermissionDenied: 요청 사용자가 태그 생성 권한이 없는 경우.
            ValidationError: 입력 데이터가 유효하지 않거나 서비스 레이어에서 발생한 값 관련 오류가 있는 경우.
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
        지정한 태그 정의를 삭제합니다.
        
        Parameters:
            pk (int | None): 삭제할 태그의 ID. None이면 404(Not Found)를 발생시킵니다.
        
        Returns:
            Response: 상태 코드 204(No Content)를 가진 응답 객체.
        
        Raises:
            NotFound: pk가 None이거나 해당 태그가 존재하지 않을 때 발생합니다.
            PermissionDenied: 요청 사용자가 태그 삭제 권한이 없을 때 발생합니다.
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
        주어진 위키의 스냅샷 목록을 반환한다.
        
        Parameters:
            wiki_pk (int | None): 조회하려는 위키의 식별자. None이면 조회할 수 없음.
        
        Returns:
            list: 직렬화된 위키 스냅샷 객체들의 리스트.
        
        Raises:
            NotFound: wiki_pk가 None이거나 해당 위키를 찾을 수 없을 때 발생한다.
        """
        if wiki_pk is None:
            raise NotFound("위키를 찾을 수 없습니다.")

        try:
            wiki = WikiService.retrieve_for_snapshots(wiki_id=wiki_pk)
        except ValueError as e:
            raise NotFound(str(e))

        serializer = WikiSnapshotSerializer(wiki.snapshots, many=True)
        return Response(serializer.data)

    def create(self, request: Request, wiki_pk: int | None = None) -> Response:
        """
        새로운 위키 스냅샷을 생성합니다.
        
        Parameters:
            wiki_pk (int | None): 스냅샷을 생성할 대상 위키의 ID.
        
        Returns:
            Response: 생성된 스냅샷의 직렬화된 표현을 담은 HTTP 응답(상태 코드 201).
        
        Raises:
            NotFound: wiki_pk가 제공되지 않았거나 해당 위키를 찾을 수 없을 때.
            PermissionDenied: 요청 사용자가 스냅샷 생성 권한이 없을 때.
            ValidationError: 입력 데이터가 유효하지 않거나 서비스에서 발생한 값 오류가 있을 때.
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
        지점(branch)에 속한 지도 목록을 페이지 단위로 반환합니다.
        
        Parameters:
            branch_pk (int | None): 목록을 조회할 지점의 ID. 제공되지 않으면 예외가 발생합니다.
        
        Returns:
            dict: 페이지네이션된 직렬화된 지도 목록 응답 데이터.
        
        Raises:
            NotFound: `branch_pk`가 None인 경우 발생합니다.
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
        새 맵 항목을 생성한다.
        
        지정한 브랜치에 대해 요청 본문을 검증하고 새 맵을 생성한 뒤 생성된 맵의 상세 직렬화 결과를 반환한다.
        
        Parameters:
            branch_pk (int | None): 생성할 대상 브랜치의 ID.
        
        Returns:
            dict: 생성된 맵의 상세 직렬화 데이터.
        
        Raises:
            NotFound: branch_pk가 제공되지 않거나 브랜치를 찾을 수 없는 경우.
            PermissionDenied: 요청 사용자가 해당 브랜치에 대해 맵 생성 권한이 없는 경우.
            ValidationError: 입력 데이터 검증 실패 또는 서비스에서 발생한 값 오류의 경우.
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
        맵의 상세 정보를 조회하며, 선택적으로 쿼리 파라미터 `currentChapter`에 따라 해당 장 기준의 스냅샷 컨텍스트를 포함합니다.
        
        Parameters:
            pk (int | None): 조회할 맵의 ID.
        
        Returns:
            Response: 직렬화된 맵 상세 데이터를 포함한 응답. `currentChapter`가 제공되면 그 장을 기준으로 한 스냅샷 정보를 포함할 수 있습니다.
        
        Raises:
            NotFound: `pk`가 없거나 해당 ID의 맵을 찾을 수 없는 경우 발생합니다.
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
        지도를 부분 수정하고 수정된 지도 상세를 반환합니다.
        
        Parameters:
            request (Request): 요청 객체, 수정할 필드들을 포함한 요청 데이터가 들어있습니다.
            pk (int | None): 수정할 지도 식별자 (map_id). 제공되지 않으면 NotFound가 발생합니다.
        
        Returns:
            Response: 수정된 지도의 상세를 직렬화한 응답 데이터.
        
        Raises:
            NotFound: `pk`가 제공되지 않거나 지도를 찾을 수 없을 때 발생합니다.
            PermissionDenied: 현재 사용자에게 수정 권한이 없을 때 발생합니다.
            ValidationError: 요청 데이터가 유효하지 않거나 서비스 레이어에서 유효성/상태 오류가 발생했을 때 발생합니다.
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
        지정한 ID의 지도를 삭제한다.
        
        삭제 권한이 없으면 PermissionDenied를 발생시키고, 해당 지도 ID가 없으면 NotFound를 발생시킨다.
        
        Parameters:
            request (Request): 요청하는 사용자 정보가 포함된 요청 객체.
            pk (int | None): 삭제할 지도 식별자.
        
        Returns:
            Response: 성공 시 HTTP 204 No Content 응답.
        
        Raises:
            NotFound: pk가 None이거나 삭제 대상 지도를 찾지 못한 경우.
            PermissionDenied: 요청 사용자가 삭제 권한이 없는 경우.
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
        """
        지도의 모든 스냅샷 목록을 직렬화한 데이터를 포함하는 응답을 반환합니다.
        
        Parameters:
            map_pk (int | None): 조회 대상 지도의 ID. None이면 NotFound가 발생합니다.
        
        Returns:
            list: 직렬화된 스냅샷 객체들의 리스트
        
        Raises:
            NotFound: map_pk가 제공되지 않았거나 해당 ID로 지도를 찾을 수 없을 때 발생합니다.
        """
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
        맵에 새 스냅샷을 생성합니다.
        
        파라미터:
            map_pk (int | None): 생성 대상 맵의 ID. None이면 NotFound를 발생시킵니다.
        
        반환값:
            dict: 생성된 스냅샷을 직렬화한 응답 데이터.
        
        발생 예외:
            NotFound: map_pk가 제공되지 않았을 때.
            PermissionDenied: 현재 사용자에게 생성 권한이 없을 때.
            ValidationError: 입력 데이터가 유효하지 않거나 내부 서비스에서 유효성 오류가 발생했을 때.
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
        스냅샷에 속한 모든 레이어를 조회하여 직렬화된 목록을 반환합니다.
        
        Parameters:
            snapshot_pk (int | None): 조회할 스냅샷의 ID.
        
        Returns:
            Response: 직렬화된 레이어 목록 데이터를 담은 응답 객체.
        
        Raises:
            NotFound: 지정한 ID의 스냅샷을 찾을 수 없을 때 발생합니다.
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
        새 맵 레이어를 생성합니다.
        
        Parameters:
            snapshot_pk (int | None): 레이어를 추가할 대상 스냅샷의 ID.
        
        Returns:
            dict: 생성된 레이어의 직렬화된 표현(응답 바디).
        
        Raises:
            NotFound: `snapshot_pk`가 제공되지 않았을 때 발생합니다.
            PermissionDenied: 사용자가 해당 스냅샷에 레이어를 추가할 권한이 없을 때 발생합니다.
            ValidationError: 입력 데이터가 유효하지 않거나 서비스 레이어에서 유효성 검사 오류가 발생할 때 발생합니다.
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
        레이어(layer_pk)에 새 지도 객체(MapObject)를 생성하고 생성된 객체의 직렬화된 데이터를 포함한 응답을 반환합니다.
        
        Parameters:
            layer_pk (int | None): 객체를 생성할 대상 레이어의 ID. None이면 NotFound가 발생합니다.
            request (Request): 요청 본문은 `MapObjectCreateSerializer`로 검증됩니다.
        
        Returns:
            Response: 생성된 지도 객체의 직렬화된 데이터와 HTTP 201 상태 코드를 가진 응답.
        
        Raises:
            NotFound: layer_pk가 제공되지 않았거나 해당 레이어를 찾을 수 없을 때 발생합니다.
            PermissionDenied: 사용자가 해당 레이어에 객체를 추가할 권한이 없을 때 발생합니다.
            ValidationError: 입력 데이터가 유효하지 않거나 서비스 레벨에서 오류가 발생했을 때 발생합니다.
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