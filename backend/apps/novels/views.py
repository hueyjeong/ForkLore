"""
Views for novels app.

Contains ViewSets for:
- Novel: CRUD operations
- Branch: List, Retrieve, Fork, Visibility, Vote, Link Request
- BranchLinkRequest: Review (approve/reject)
"""

from django.db import IntegrityError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from common.pagination import StandardPagination
from .models import Novel, Branch, BranchLinkRequest, BranchVisibility, LinkRequestStatus
from .services import NovelService, BranchService, BranchLinkService
from .serializers import (
    NovelCreateSerializer,
    NovelDetailSerializer,
    NovelListSerializer,
    NovelUpdateSerializer,
    BranchCreateSerializer,
    BranchDetailSerializer,
    BranchListSerializer,
    BranchVisibilityUpdateSerializer,
    BranchLinkRequestCreateSerializer,
    BranchLinkRequestReviewSerializer,
    BranchLinkRequestSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="소설 목록 조회"),
    retrieve=extend_schema(summary="소설 상세 조회"),
    create=extend_schema(summary="소설 생성"),
    partial_update=extend_schema(summary="소설 수정"),
    destroy=extend_schema(summary="소설 삭제"),
)
class NovelViewSet(viewsets.ViewSet):
    """ViewSet for Novel CRUD operations."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = NovelService()

    def list(self, request):
        """List novels with optional filtering and sorting."""
        filters = {}
        if "genre" in request.query_params:
            filters["genre"] = request.query_params["genre"]
        if "status" in request.query_params:
            filters["status"] = request.query_params["status"]

        sort = request.query_params.get("sort", "latest")

        novels = self.service.list(filters=filters if filters else None, sort=sort)

        # Apply pagination
        paginator = StandardPagination()
        page = paginator.paginate_queryset(novels, request)
        if page is not None:
            serializer = NovelListSerializer(page, many=True)
            return Response(
                {
                    "success": True,
                    "message": None,
                    "data": {
                        "results": serializer.data,
                        "count": paginator.page.paginator.count,
                        "next": paginator.get_next_link(),
                        "previous": paginator.get_previous_link(),
                    },
                }
            )

        serializer = NovelListSerializer(novels, many=True)
        return Response({"success": True, "message": None, "data": {"results": serializer.data}})

    def retrieve(self, request, pk=None):
        """Retrieve a single novel."""
        try:
            novel = self.service.retrieve(novel_id=pk)
            serializer = NovelDetailSerializer(novel)
            return Response({"success": True, "message": None, "data": serializer.data})
        except Novel.DoesNotExist:
            return Response(
                {"success": False, "message": "소설을 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request):
        """Create a new novel."""
        serializer = NovelCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "유효하지 않은 데이터", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            novel = self.service.create(author=request.user, data=serializer.validated_data)
            return Response(
                {"success": True, "message": None, "data": NovelDetailSerializer(novel).data},
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def partial_update(self, request, pk=None):
        """Update a novel."""
        serializer = NovelUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "유효하지 않은 데이터", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            novel = self.service.update(
                novel_id=pk, author=request.user, data=serializer.validated_data
            )
            return Response(
                {"success": True, "message": None, "data": NovelDetailSerializer(novel).data}
            )
        except Novel.DoesNotExist:
            return Response(
                {"success": False, "message": "소설을 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        except PermissionError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )

    def destroy(self, request, pk=None):
        """Delete a novel."""
        try:
            self.service.delete(novel_id=pk, author=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Novel.DoesNotExist:
            return Response(
                {"success": False, "message": "소설을 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        except PermissionError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )


@extend_schema_view(
    list=extend_schema(
        summary="브랜치 목록 조회",
        parameters=[
            OpenApiParameter(name="visibility", type=str, description="Filter by visibility"),
            OpenApiParameter(name="sort", type=str, description="Sort by: votes, latest, views"),
        ],
    ),
    retrieve=extend_schema(summary="브랜치 상세 조회"),
)
class BranchViewSet(viewsets.ViewSet):
    """ViewSet for Branch operations."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = BranchService()
        self.link_service = BranchLinkService()

    def list(self, request, novel_pk=None):
        """List branches for a novel."""
        visibility = request.query_params.get("visibility")
        sort = request.query_params.get("sort", "latest")

        branches = self.service.list(novel_id=novel_pk, visibility=visibility, sort=sort)
        serializer = BranchListSerializer(branches, many=True)

        return Response({"success": True, "message": None, "data": {"results": serializer.data}})

    def create(self, request, novel_pk=None):
        """Fork a new branch."""
        serializer = BranchCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "유효하지 않은 데이터", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        parent_branch_id = request.data.get("parent_branch_id")
        if not parent_branch_id:
            return Response(
                {"success": False, "message": "parent_branch_id는 필수입니다.", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            branch = self.service.fork(
                novel_id=novel_pk,
                parent_branch_id=parent_branch_id,
                author=request.user,
                data=serializer.validated_data,
            )
            return Response(
                {"success": True, "message": None, "data": BranchDetailSerializer(branch).data},
                status=status.HTTP_201_CREATED,
            )
        except PermissionError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )
        except (Novel.DoesNotExist, Branch.DoesNotExist):
            return Response(
                {"success": False, "message": "소설 또는 브랜치를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"], url_path="main")
    def main(self, request, novel_pk=None):
        """Get main branch of a novel."""
        try:
            branch = self.service.get_main_branch(novel_id=novel_pk)
            return Response(
                {"success": True, "message": None, "data": BranchDetailSerializer(branch).data}
            )
        except Branch.DoesNotExist:
            return Response(
                {"success": False, "message": "메인 브랜치를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

    def retrieve(self, request, pk=None, novel_pk=None):
        """Retrieve a single branch."""
        try:
            branch = self.service.retrieve(branch_id=pk)
            return Response(
                {"success": True, "message": None, "data": BranchDetailSerializer(branch).data}
            )
        except Branch.DoesNotExist:
            return Response(
                {"success": False, "message": "브랜치를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )


class BranchDetailViewSet(viewsets.ViewSet):
    """ViewSet for single branch operations (visibility, vote, link-request)."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = BranchService()
        self.link_service = BranchLinkService()

    def retrieve(self, request, pk=None):
        """Retrieve a single branch."""
        try:
            branch = self.service.retrieve(branch_id=pk)
            return Response(
                {"success": True, "message": None, "data": BranchDetailSerializer(branch).data}
            )
        except Branch.DoesNotExist:
            return Response(
                {"success": False, "message": "브랜치를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(
        detail=True, methods=["patch"], url_path="visibility", permission_classes=[IsAuthenticated]
    )
    def visibility(self, request, pk=None):
        """Update branch visibility."""
        serializer = BranchVisibilityUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "유효하지 않은 데이터", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            branch = self.service.update_visibility(
                branch_id=pk,
                author=request.user,
                visibility=serializer.validated_data["visibility"],
            )
            return Response(
                {"success": True, "message": None, "data": BranchDetailSerializer(branch).data}
            )
        except Branch.DoesNotExist:
            return Response(
                {"success": False, "message": "브랜치를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        except PermissionError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="vote",
        permission_classes=[IsAuthenticated],
    )
    def vote(self, request, pk=None):
        """Add or remove a vote."""
        try:
            if request.method == "POST":
                self.service.vote(branch_id=pk, user=request.user)
                return Response(
                    {"success": True, "message": "투표 완료", "data": None},
                    status=status.HTTP_201_CREATED,
                )
            else:  # DELETE
                result = self.service.unvote(branch_id=pk, user=request.user)
                if result:
                    return Response(status=status.HTTP_204_NO_CONTENT)
                return Response(
                    {"success": False, "message": "투표 기록이 없습니다.", "data": None},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except Branch.DoesNotExist:
            return Response(
                {"success": False, "message": "브랜치를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        except IntegrityError:
            return Response(
                {"success": False, "message": "이미 투표하셨습니다.", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=True, methods=["post"], url_path="link-request", permission_classes=[IsAuthenticated]
    )
    def link_request(self, request, pk=None):
        """Create a link request."""
        serializer = BranchLinkRequestCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "유효하지 않은 데이터", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            link_request = self.link_service.request_link(
                branch_id=pk,
                requester=request.user,
                message=serializer.validated_data.get("request_message", ""),
            )
            return Response(
                {
                    "success": True,
                    "message": None,
                    "data": BranchLinkRequestSerializer(link_request).data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Branch.DoesNotExist:
            return Response(
                {"success": False, "message": "브랜치를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        except PermissionError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=True,
        methods=["get"],
        url_path="continue-reading",
        permission_classes=[IsAuthenticated],
    )
    def continue_reading(self, request, pk=None):
        """Get continue reading info for this branch."""
        from apps.interactions.services import ReadingService
        from apps.interactions.serializers import ContinueReadingSerializer

        try:
            branch = Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            return Response(
                {"success": False, "message": "브랜치를 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        result = ReadingService.get_continue_reading(user=request.user, branch_id=pk)
        serializer = ContinueReadingSerializer(result)
        return Response(serializer.data)


class LinkRequestViewSet(viewsets.ViewSet):
    """ViewSet for BranchLinkRequest operations."""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = BranchLinkService()

    def partial_update(self, request, pk=None):
        """Review (approve/reject) a link request."""
        serializer = BranchLinkRequestReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "유효하지 않은 데이터", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        status_value = serializer.validated_data["status"]
        comment = serializer.validated_data.get("review_comment", "")

        try:
            if status_value == LinkRequestStatus.APPROVED:
                link_request = self.service.approve_link(
                    request_id=pk, reviewer=request.user, comment=comment
                )
            else:
                link_request = self.service.reject_link(
                    request_id=pk, reviewer=request.user, comment=comment
                )

            return Response(
                {
                    "success": True,
                    "message": None,
                    "data": BranchLinkRequestSerializer(link_request).data,
                }
            )
        except BranchLinkRequest.DoesNotExist:
            return Response(
                {"success": False, "message": "연결 요청을 찾을 수 없습니다.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        except PermissionError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )
