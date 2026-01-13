"""
Services for novels app.

Contains:
- NovelService: Business logic for novel operations
- BranchService: Business logic for branch operations
"""

from django.db import transaction
from django.db.models import QuerySet, F

from django.utils import timezone

from .models import (
    Novel,
    Branch,
    BranchType,
    BranchVisibility,
    CanonStatus,
    BranchVote,
    BranchLinkRequest,
    LinkRequestStatus,
    Genre,
    AgeRating,
    NovelStatus,
)


class NovelService:
    """Service class for Novel-related business logic."""

    @transaction.atomic
    def create(self, author, data: dict) -> Novel:
        """
        Create a new novel with automatic main branch creation.

        Args:
            author: The user creating the novel
            data: Dict containing novel fields (title, description, genre, etc.)

        Returns:
            Created Novel instance

        Raises:
            ValueError/KeyError: If required fields are missing
        """
        # Validate required fields
        if "title" not in data or not data["title"]:
            raise ValueError("제목은 필수입니다.")

        novel = Novel.objects.create(
            author=author,
            title=data["title"],
            description=data.get("description", ""),
            cover_image_url=data.get("cover_image_url", ""),
            genre=data.get("genre", Genre.FANTASY),
            age_rating=data.get("age_rating", AgeRating.ALL),
            status=data.get("status", NovelStatus.ONGOING),
            allow_branching=data.get("allow_branching", True),
        )

        # Auto-create main branch
        Branch.objects.create(
            novel=novel,
            author=author,
            name=novel.title,
            is_main=True,
            branch_type=BranchType.MAIN,
            visibility=BranchVisibility.PUBLIC,
        )

        return novel

    def list(
        self,
        filters: dict | None = None,
        sort: str | None = None,
    ) -> QuerySet[Novel]:
        """
        List novels with optional filtering and sorting.

        Args:
            filters: Dict of filter conditions (genre, status, author, etc.)
            sort: Sort order ("popular", "latest", "likes")

        Returns:
            QuerySet of novels
        """
        queryset = Novel.objects.filter(deleted_at__isnull=True)

        if filters:
            if "genre" in filters:
                queryset = queryset.filter(genre=filters["genre"])
            if "status" in filters:
                queryset = queryset.filter(status=filters["status"])
            if "author" in filters:
                queryset = queryset.filter(author=filters["author"])
            if "age_rating" in filters:
                queryset = queryset.filter(age_rating=filters["age_rating"])

        # Apply sorting
        if sort == "popular":
            queryset = queryset.order_by("-total_view_count")
        elif sort == "likes":
            queryset = queryset.order_by("-total_like_count")
        else:  # default: latest
            queryset = queryset.order_by("-created_at")

        return queryset

    def retrieve(self, novel_id: int) -> Novel:
        """
        Retrieve a single novel by ID.

        Args:
            novel_id: The novel's primary key

        Returns:
            Novel instance

        Raises:
            Novel.DoesNotExist: If novel not found or is deleted
        """
        return Novel.objects.get(id=novel_id, deleted_at__isnull=True)

    @transaction.atomic
    def update(self, novel_id: int, author, data: dict) -> Novel:
        """
        Update an existing novel.

        Args:
            novel_id: The novel's primary key
            author: The user attempting the update
            data: Dict of fields to update

        Returns:
            Updated Novel instance

        Raises:
            Novel.DoesNotExist: If novel not found
            PermissionError: If user is not the author
        """
        novel = Novel.objects.get(id=novel_id, deleted_at__isnull=True)

        if novel.author != author:
            raise PermissionError("소설 수정 권한이 없습니다.")

        # Update allowed fields
        allowed_fields = [
            "title",
            "description",
            "cover_image_url",
            "genre",
            "age_rating",
            "status",
            "allow_branching",
        ]

        for field in allowed_fields:
            if field in data:
                setattr(novel, field, data[field])

        novel.save()
        return novel

    @transaction.atomic
    def delete(self, novel_id: int, author) -> None:
        """
        Soft-delete a novel.

        Args:
            novel_id: The novel's primary key
            author: The user attempting the deletion

        Raises:
            Novel.DoesNotExist: If novel not found or already deleted
            PermissionError: If user is not the author
        """
        novel = Novel.objects.get(id=novel_id, deleted_at__isnull=True)

        if novel.author != author:
            raise PermissionError("소설 삭제 권한이 없습니다.")

        novel.soft_delete()


class BranchService:
    """Service class for Branch-related business logic."""

    def list(
        self,
        novel_id: int,
        visibility: str | None = None,
        sort: str | None = None,
    ) -> QuerySet[Branch]:
        """
        List branches for a novel with optional filtering and sorting.

        Args:
            novel_id: The novel's primary key
            visibility: Filter by visibility (PRIVATE, PUBLIC, LINKED)
            sort: Sort order ("votes", "latest", "views")

        Returns:
            QuerySet of branches
        """
        queryset = Branch.objects.filter(novel_id=novel_id, deleted_at__isnull=True)

        if visibility:
            queryset = queryset.filter(visibility=visibility)

        # Apply sorting
        if sort == "votes":
            queryset = queryset.order_by("-vote_count")
        elif sort == "views":
            queryset = queryset.order_by("-view_count")
        else:  # default: latest
            queryset = queryset.order_by("-created_at")

        return queryset

    def retrieve(self, branch_id: int) -> Branch:
        """
        Retrieve a single branch by ID.

        Args:
            branch_id: The branch's primary key

        Returns:
            Branch instance

        Raises:
            Branch.DoesNotExist: If branch not found or is deleted
        """
        return Branch.objects.get(id=branch_id, deleted_at__isnull=True)

    def get_main_branch(self, novel_id: int) -> Branch:
        """
        Get the main branch of a novel.

        Args:
            novel_id: The novel's primary key

        Returns:
            Main Branch instance

        Raises:
            Branch.DoesNotExist: If no main branch found
        """
        return Branch.objects.get(novel_id=novel_id, is_main=True, deleted_at__isnull=True)

    @transaction.atomic
    def fork(
        self,
        novel_id: int,
        parent_branch_id: int,
        author,
        data: dict,
    ) -> Branch:
        """
        Create a forked branch from a parent branch.

        Args:
            novel_id: The novel's primary key
            parent_branch_id: The parent branch's primary key
            author: The user creating the fork
            data: Dict containing branch fields (name, description, etc.)

        Returns:
            Created Branch instance

        Raises:
            PermissionError: If novel doesn't allow branching
            ValueError: If required fields are missing
        """
        novel = Novel.objects.get(id=novel_id, deleted_at__isnull=True)

        if not novel.allow_branching:
            raise PermissionError("이 소설은 브랜치 생성이 허용되지 않습니다.")

        if "name" not in data or not data["name"]:
            raise ValueError("브랜치 이름은 필수입니다.")

        parent_branch = Branch.objects.get(id=parent_branch_id, deleted_at__isnull=True)

        branch = Branch.objects.create(
            novel=novel,
            author=author,
            parent_branch=parent_branch,
            name=data["name"],
            description=data.get("description", ""),
            cover_image_url=data.get("cover_image_url", ""),
            branch_type=data.get("branch_type", BranchType.FAN_FIC),
            fork_point_chapter=data.get("fork_point_chapter"),
            is_main=False,
            visibility=BranchVisibility.PRIVATE,
            canon_status=CanonStatus.NON_CANON,
        )

        # Increment novel's branch_count
        Novel.objects.filter(id=novel_id).update(branch_count=F("branch_count") + 1)

        return branch

    @transaction.atomic
    def update_visibility(
        self,
        branch_id: int,
        author,
        visibility: str,
    ) -> Branch:
        """
        Update branch visibility.

        Args:
            branch_id: The branch's primary key
            author: The user attempting the update
            visibility: New visibility value

        Returns:
            Updated Branch instance

        Raises:
            PermissionError: If user is not the owner
            ValueError: If trying to change main branch visibility
        """
        branch = Branch.objects.get(id=branch_id, deleted_at__isnull=True)

        if branch.author != author:
            raise PermissionError("브랜치 수정 권한이 없습니다.")

        if branch.is_main:
            raise ValueError("메인 브랜치의 공개 상태는 변경할 수 없습니다.")

        old_visibility = branch.visibility
        branch.visibility = visibility
        branch.save()

        # Update novel's linked_branch_count if visibility changed to/from LINKED
        if old_visibility != visibility:
            if visibility == BranchVisibility.LINKED:
                Novel.objects.filter(id=branch.novel_id).update(
                    linked_branch_count=F("linked_branch_count") + 1
                )
            elif old_visibility == BranchVisibility.LINKED:
                Novel.objects.filter(id=branch.novel_id).update(
                    linked_branch_count=F("linked_branch_count") - 1
                )

        return branch

    @transaction.atomic
    def vote(self, branch_id: int, user) -> bool:
        """
        Add a vote to a branch.

        Args:
            branch_id: The branch's primary key
            user: The user voting

        Returns:
            True if vote was created

        Raises:
            IntegrityError: If user already voted
        """
        branch = Branch.objects.get(id=branch_id, deleted_at__isnull=True)

        BranchVote.objects.create(user=user, branch=branch)

        Branch.objects.filter(id=branch_id).update(vote_count=F("vote_count") + 1)

        return True

    @transaction.atomic
    def unvote(self, branch_id: int, user) -> bool:
        """
        Remove a vote from a branch.

        Args:
            branch_id: The branch's primary key
            user: The user removing vote

        Returns:
            True if vote was removed, False if no vote existed
        """
        deleted_count, _ = BranchVote.objects.filter(user=user, branch_id=branch_id).delete()

        if deleted_count > 0:
            Branch.objects.filter(id=branch_id, vote_count__gt=0).update(
                vote_count=F("vote_count") - 1
            )
            return True

        return False


class BranchLinkService:
    """Service class for Branch Link Request operations."""

    def request_link(
        self,
        branch_id: int,
        requester,
        message: str = "",
    ) -> BranchLinkRequest:
        """
        Create a link request for a branch.

        Args:
            branch_id: The branch's primary key
            requester: The user making the request
            message: Optional request message

        Returns:
            Created BranchLinkRequest instance

        Raises:
            PermissionError: If requester is not the branch author
            ValueError: If branch is main, already linked, or has pending request
        """
        branch = Branch.objects.get(id=branch_id, deleted_at__isnull=True)

        if branch.author != requester:
            raise PermissionError("브랜치 작성자만 연결 요청을 할 수 있습니다.")

        if branch.is_main:
            raise ValueError("메인 브랜치는 연결 요청을 할 수 없습니다.")

        if branch.visibility == BranchVisibility.LINKED:
            raise ValueError("이미 연결된 브랜치입니다.")

        # Check for pending request
        if BranchLinkRequest.objects.filter(
            branch=branch, status=LinkRequestStatus.PENDING
        ).exists():
            raise ValueError("대기중인 요청이 이미 존재합니다.")

        return BranchLinkRequest.objects.create(
            branch=branch,
            status=LinkRequestStatus.PENDING,
            request_message=message,
        )

    @transaction.atomic
    def approve_link(
        self,
        request_id: int,
        reviewer,
        comment: str = "",
    ) -> BranchLinkRequest:
        """
        Approve a link request (original author only).

        Args:
            request_id: The link request's primary key
            reviewer: The user approving (must be novel author)
            comment: Optional review comment

        Returns:
            Updated BranchLinkRequest instance

        Raises:
            PermissionError: If reviewer is not the novel author
            ValueError: If request is not pending
        """
        link_request = BranchLinkRequest.objects.select_related("branch__novel").get(id=request_id)

        if link_request.branch.novel.author != reviewer:
            raise PermissionError("원작 작가만 연결 요청을 승인할 수 있습니다.")

        if link_request.status != LinkRequestStatus.PENDING:
            raise ValueError("대기중인 요청만 승인할 수 있습니다.")

        # Update request
        link_request.status = LinkRequestStatus.APPROVED
        link_request.reviewer = reviewer
        link_request.review_comment = comment
        link_request.reviewed_at = timezone.now()
        link_request.save()

        # Update branch visibility to LINKED
        branch = link_request.branch
        branch.visibility = BranchVisibility.LINKED
        branch.save()

        # Increment novel's linked_branch_count
        Novel.objects.filter(id=branch.novel_id).update(
            linked_branch_count=F("linked_branch_count") + 1
        )

        return link_request

    @transaction.atomic
    def reject_link(
        self,
        request_id: int,
        reviewer,
        comment: str = "",
    ) -> BranchLinkRequest:
        """
        Reject a link request (original author only).

        Args:
            request_id: The link request's primary key
            reviewer: The user rejecting (must be novel author)
            comment: Optional review comment

        Returns:
            Updated BranchLinkRequest instance

        Raises:
            PermissionError: If reviewer is not the novel author
            ValueError: If request is not pending
        """
        link_request = BranchLinkRequest.objects.select_related("branch__novel").get(id=request_id)

        if link_request.branch.novel.author != reviewer:
            raise PermissionError("원작 작가만 연결 요청을 거절할 수 있습니다.")

        if link_request.status != LinkRequestStatus.PENDING:
            raise ValueError("대기중인 요청만 거절할 수 있습니다.")

        # Update request
        link_request.status = LinkRequestStatus.REJECTED
        link_request.reviewer = reviewer
        link_request.review_comment = comment
        link_request.reviewed_at = timezone.now()
        link_request.save()

        return link_request

    def list_requests(
        self,
        branch_id: int,
        status: str | None = None,
    ) -> QuerySet[BranchLinkRequest]:
        """
        List link requests for a branch.

        Args:
            branch_id: The branch's primary key
            status: Optional filter by status

        Returns:
            QuerySet of BranchLinkRequest
        """
        queryset = BranchLinkRequest.objects.filter(branch_id=branch_id)

        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by("-created_at")
