"""
Views for novels app.

Contains ViewSets for:
- Novel: CRUD operations
- Branch: List, Retrieve, Fork, Visibility, Vote, Link Request
- BranchLinkRequest: Review (approve/reject)
"""

from django.db import IntegrityError
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response

from common.pagination import StandardPagination

from .models import Branch, BranchLinkRequest, LinkRequestStatus, Novel
from .serializers import (
    BranchCreateSerializer,
    BranchDetailSerializer,
    BranchLinkRequestCreateSerializer,
    BranchLinkRequestReviewSerializer,
    BranchLinkRequestSerializer,
    BranchListSerializer,
    BranchVisibilityUpdateSerializer,
    NovelCreateSerializer,
    NovelDetailSerializer,
    NovelListSerializer,
    NovelUpdateSerializer,
)
from .services import BranchLinkService, BranchService, NovelService


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

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.service = NovelService()

    def list(self, request: Request) -> Response:
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
            return paginator.get_paginated_response(serializer.data)

        serializer = NovelListSerializer(novels, many=True)
        return Response({"results": serializer.data})

    def retrieve(self, request: Request, pk: int | None = None) -> Response:
        """Retrieve a single novel."""
        try:
            novel = self.service.retrieve(novel_id=pk)
            serializer = NovelDetailSerializer(novel)
            return Response(serializer.data)
        except Novel.DoesNotExist:
            raise NotFound("소설을 찾을 수 없습니다.")

    def create(self, request: Request) -> Response:
        """Create a new novel."""
        serializer = NovelCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            novel = self.service.create(author=request.user, data=serializer.validated_data)
            return Response(
                NovelDetailSerializer(novel).data,
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            raise ValidationError(str(e))

    def partial_update(self, request: Request, pk: int | None = None) -> Response:
        """Update a novel."""
        serializer = NovelUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            novel = self.service.update(
                novel_id=pk, author=request.user, data=serializer.validated_data
            )
            return Response(NovelDetailSerializer(novel).data)
        except Novel.DoesNotExist:
            raise NotFound("소설을 찾을 수 없습니다.")
        except PermissionError as e:
            raise PermissionDenied(str(e))

    def destroy(self, request: Request, pk: int | None = None) -> Response:
        """Delete a novel."""
        try:
            self.service.delete(novel_id=pk, author=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Novel.DoesNotExist:
            raise NotFound("소설을 찾을 수 없습니다.")
        except PermissionError as e:
            raise PermissionDenied(str(e))


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

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.service = BranchService()
        self.link_service = BranchLinkService()

    def list(self, request: Request, novel_pk: int | None = None) -> Response:
        """List branches for a novel."""
        visibility = request.query_params.get("visibility")
        sort = request.query_params.get("sort", "latest")

        branches = self.service.list(novel_id=novel_pk, visibility=visibility, sort=sort)
        serializer = BranchListSerializer(branches, many=True)

        return Response({"results": serializer.data})

    def create(self, request: Request, novel_pk: int | None = None) -> Response:
        """Fork a new branch."""
        serializer = BranchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        parent_branch_id = request.data.get("parent_branch_id")
        if not parent_branch_id:
            raise ValidationError("parent_branch_id는 필수입니다.")

        try:
            branch = self.service.fork(
                novel_id=novel_pk,
                parent_branch_id=parent_branch_id,
                author=request.user,
                data=serializer.validated_data,
            )
            return Response(
                BranchDetailSerializer(branch).data,
                status=status.HTTP_201_CREATED,
            )
        except PermissionError as e:
            raise PermissionDenied(str(e))
        except (Novel.DoesNotExist, Branch.DoesNotExist):
            raise NotFound("소설 또는 브랜치를 찾을 수 없습니다.")
        except ValueError as e:
            raise ValidationError(str(e))

    @action(detail=False, methods=["get"], url_path="main")
    def main(self, request: Request, novel_pk: int | None = None) -> Response:
        """Get main branch of a novel."""
        try:
            branch = self.service.get_main_branch(novel_id=novel_pk)
            return Response(BranchDetailSerializer(branch).data)
        except Branch.DoesNotExist:
            raise NotFound("메인 브랜치를 찾을 수 없습니다.")

    def retrieve(
        self, request: Request, pk: int | None = None, novel_pk: int | None = None
    ) -> Response:
        """Retrieve a single branch."""
        try:
            branch = self.service.retrieve(branch_id=pk)
            return Response(BranchDetailSerializer(branch).data)
        except Branch.DoesNotExist:
            raise NotFound("브랜치를 찾을 수 없습니다.")


class BranchDetailViewSet(viewsets.ViewSet):
    """ViewSet for single branch operations (visibility, vote, link-request)."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.service = BranchService()
        self.link_service = BranchLinkService()

    def retrieve(self, request: Request, pk: int | None = None) -> Response:
        """Retrieve a single branch."""
        try:
            branch = self.service.retrieve(branch_id=pk)
            return Response(BranchDetailSerializer(branch).data)
        except Branch.DoesNotExist:
            raise NotFound("브랜치를 찾을 수 없습니다.")

    @action(
        detail=True, methods=["patch"], url_path="visibility", permission_classes=[IsAuthenticated]
    )
    def visibility(self, request: Request, pk: int | None = None) -> Response:
        """Update branch visibility."""
        serializer = BranchVisibilityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            branch = self.service.update_visibility(
                branch_id=pk,
                author=request.user,
                visibility=serializer.validated_data["visibility"],
            )
            return Response(BranchDetailSerializer(branch).data)
        except Branch.DoesNotExist:
            raise NotFound("브랜치를 찾을 수 없습니다.")
        except PermissionError as e:
            raise PermissionDenied(str(e))
        except ValueError as e:
            raise ValidationError(str(e))

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="vote",
        permission_classes=[IsAuthenticated],
    )
    def vote(self, request: Request, pk: int | None = None) -> Response:
        """Add or remove a vote."""
        try:
            if request.method == "POST":
                self.service.vote(branch_id=pk, user=request.user)
                return Response(
                    {"message": "투표 완료"},
                    status=status.HTTP_201_CREATED,
                )
            else:  # DELETE
                result = self.service.unvote(branch_id=pk, user=request.user)
                if result:
                    return Response(status=status.HTTP_204_NO_CONTENT)
                raise NotFound("투표 기록이 없습니다.")
        except Branch.DoesNotExist:
            raise NotFound("브랜치를 찾을 수 없습니다.")
        except IntegrityError:
            raise ValidationError("이미 투표하셨습니다.")

    @action(
        detail=True, methods=["post"], url_path="link-request", permission_classes=[IsAuthenticated]
    )
    def link_request(self, request: Request, pk: int | None = None) -> Response:
        """Create a link request."""
        serializer = BranchLinkRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            link_request = self.link_service.request_link(
                branch_id=pk,
                requester=request.user,
                message=serializer.validated_data.get("request_message", ""),
            )
            return Response(
                BranchLinkRequestSerializer(link_request).data,
                status=status.HTTP_201_CREATED,
            )
        except Branch.DoesNotExist:
            raise NotFound("브랜치를 찾을 수 없습니다.")
        except PermissionError as e:
            raise PermissionDenied(str(e))
        except ValueError as e:
            raise ValidationError(str(e))

    @action(
        detail=True,
        methods=["get"],
        url_path="continue-reading",
        permission_classes=[IsAuthenticated],
    )
    def continue_reading(self, request: Request, pk: int | None = None) -> Response:
        """Get continue reading info for this branch."""
        from apps.interactions.serializers import ContinueReadingSerializer
        from apps.interactions.services import ReadingService

        try:
            Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            raise NotFound("브랜치를 찾을 수 없습니다.")

        result = ReadingService.get_continue_reading(user=request.user, branch_id=pk)
        serializer = ContinueReadingSerializer(result)
        return Response(serializer.data)


class LinkRequestViewSet(viewsets.ViewSet):
    """ViewSet for BranchLinkRequest operations."""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.service = BranchLinkService()

    def partial_update(self, request: Request, pk: int | None = None) -> Response:
        """Review (approve/reject) a link request."""
        serializer = BranchLinkRequestReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

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

            return Response(BranchLinkRequestSerializer(link_request).data)
        except BranchLinkRequest.DoesNotExist:
            raise NotFound("연결 요청을 찾을 수 없습니다.")
        except PermissionError as e:
            raise PermissionDenied(str(e))
        except ValueError as e:
            raise ValidationError(str(e))
