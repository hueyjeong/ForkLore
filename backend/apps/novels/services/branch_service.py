from django.db import transaction
from django.db.models import F, QuerySet
from django.utils import timezone

from apps.users.models import User
from common.exceptions import ConflictError

from ..models import (
    Branch,
    BranchLinkRequest,
    BranchType,
    BranchVisibility,
    BranchVote,
    CanonStatus,
    LinkRequestStatus,
    Novel,
)


class BranchService:
    """Service class for Branch-related business logic."""

    def list(
        self,
        novel_id: int,
        visibility: str | None = None,
        sort: str | None = None,
    ) -> QuerySet[Branch]:
        """
        List branches for a novel with optional visibility filtering and sorting.
        
        Parameters:
            novel_id (int): Primary key of the novel to list branches for.
            visibility (str | None): Optional visibility filter; expected values include "PRIVATE", "PUBLIC", or "LINKED".
            sort (str | None): Optional sort key: "votes" (by vote_count), "views" (by view_count), or any other value for latest (by created_at).
        
        Returns:
            QuerySet[Branch]: QuerySet of non-deleted Branch objects for the novel, with author relation eager-loaded.
        """
        queryset = Branch.objects.filter(novel_id=novel_id, deleted_at__isnull=True).select_related(
            "author"
        )

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
        author: User,
        data: dict,
        parent_version: int | None = None,
    ) -> Branch:
        """
        Create a forked branch from a parent branch.
        
        Parameters:
            novel_id (int): ID of the novel to fork within.
            parent_branch_id (int): ID of the parent branch to fork from.
            author (User): User creating the new branch.
            data (dict): Branch fields; must include `name`. May include `description`, `cover_image_url`, `branch_type`, `fork_point_chapter`.
            parent_version (int | None): Optional optimistic-locking version expected for the parent branch.
        
        Returns:
            Branch: The newly created Branch instance.
        
        Raises:
            PermissionError: If the novel does not allow branching.
            ValueError: If required data is missing (e.g., `name`).
            ConflictError: If `parent_version` is provided and does not match the parent's current version.
        """
        novel = Novel.objects.get(id=novel_id, deleted_at__isnull=True)

        if not novel.allow_branching:
            raise PermissionError("이 소설은 브랜치 생성이 허용되지 않습니다.")

        if "name" not in data or not data["name"]:
            raise ValueError("브랜치 이름은 필수입니다.")

        parent_branch = Branch.objects.get(id=parent_branch_id, deleted_at__isnull=True)

        if parent_version is not None and parent_branch.version != parent_version:
            raise ConflictError("브랜치 버전이 변경되었습니다. 최신 상태를 확인해주세요.")

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
    def update(
        self,
        branch_id: int,
        author: User,
        data: dict,
    ) -> Branch:
        """
        Update mutable fields of an existing branch owned by the specified author.
        
        Only the `name`, `description`, and `cover_image_url` keys in `data` are applied when present. The branch's `version` is incremented and the saved, refreshed Branch instance is returned.
        
        Parameters:
            branch_id (int): Primary key of the branch to update.
            author (User): User attempting the update; must be the branch owner.
            data (dict): Dict containing fields to update; supported keys: `name`, `description`, `cover_image_url`.
        
        Returns:
            Branch: The updated Branch instance with an incremented `version`.
        
        Raises:
            PermissionError: If `author` is not the branch owner.
        """
        branch = Branch.objects.get(id=branch_id, deleted_at__isnull=True)

        if branch.author != author:
            raise PermissionError("브랜치 수정 권한이 없습니다.")

        if "name" in data:
            branch.name = data["name"]
        if "description" in data:
            branch.description = data["description"]
        if "cover_image_url" in data:
            branch.cover_image_url = data["cover_image_url"]

        branch.version = F("version") + 1
        branch.save()
        branch.refresh_from_db()
        return branch

    @transaction.atomic
    def update_visibility(
        self,
        branch_id: int,
        author: User,
        visibility: str,
    ) -> Branch:
        """
        Change a branch's visibility, increment its version, and adjust the novel's linked-branch counter when needed.
        
        Args:
            branch_id (int): Primary key of the branch to update (only non-deleted branches are considered).
            author (User): User attempting the update; must be the branch's owner.
            visibility (str): New visibility value to apply.
        
        Returns:
            Branch: The updated Branch instance (refreshed from the database).
        
        Raises:
            Branch.DoesNotExist: If no non-deleted branch with the given id exists.
            PermissionError: If the provided author is not the branch owner.
            ValueError: If attempting to change the visibility of the main branch.
        """
        branch = Branch.objects.get(id=branch_id, deleted_at__isnull=True)

        if branch.author != author:
            raise PermissionError("브랜치 수정 권한이 없습니다.")

        if branch.is_main:
            raise ValueError("메인 브랜치의 공개 상태는 변경할 수 없습니다.")

        old_visibility = branch.visibility
        branch.visibility = visibility
        branch.version = F("version") + 1
        branch.save()
        branch.refresh_from_db()

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
    def vote(self, branch_id: int, user: User) -> bool:
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
    def unvote(self, branch_id: int, user: User) -> bool:
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
        requester: User,
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
        reviewer: User,
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
        reviewer: User,
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