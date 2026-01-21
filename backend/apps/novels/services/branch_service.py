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
        소설의 삭제되지 않은 브랜치들을 선택한 가시성 필터와 정렬 기준으로 반환한다.
        
        Parameters:
            novel_id (int): 대상 소설의 기본 키.
            visibility (str | None): 선택적 필터. 허용 값: "PRIVATE", "PUBLIC", "LINKED".
            sort (str | None): 정렬 기준. 허용 값: "votes" (투표수 내림차순), "views" (조회수 내림차순), 기본은 최신순 ("created_at" 내림차순).
        
        Returns:
            QuerySet[Branch]: 요청 조건에 맞는 Branch 인스턴스들의 쿼리셋(삭제된 항목 제외).
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
        부모 브랜치로부터 새 포크 브랜치를 생성합니다.
        
        Parameters:
            novel_id (int): 대상 소설의 PK.
            parent_branch_id (int): 포크할 부모 브랜치의 PK.
            author (User): 포크를 생성하는 사용자.
            data (dict): 생성할 브랜치의 필드(예: name, description, cover_image_url 등).
            parent_version (int | None): 부모 브랜치의 기대 버전(낙관적 락 검증에 사용).
        
        Returns:
            Branch: 생성된 Branch 인스턴스.
        
        Raises:
            PermissionError: 해당 소설에서 브랜치 생성이 허용되지 않을 때.
            ValueError: 필수 필드(예: name)가 누락되거나 유효하지 않을 때.
            ConflictError: 제공된 parent_version과 부모 브랜치의 현재 버전이 일치하지 않을 때.
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
        브랜치의 이름, 설명, 표지 URL을 업데이트하고 필요할 경우 버전을 증분하여 저장한다.
        
        Parameters:
            branch_id (int): 업데이트할 브랜치의 식별자
            author (User): 업데이트를 시도하는 사용자 (브랜치 소유자여야 함)
            data (dict): 업데이트할 필드. 허용되는 키: `"name"`, `"description"`, `"cover_image_url"`
        
        Returns:
            Branch: 변경된 내용이 반영된 브랜치 인스턴스 (필드 변경 시 `version`이 1 증가함)
        
        Raises:
            PermissionError: 요청한 사용자가 브랜치 소유자가 아닐 경우
            ValueError: `name` 필드를 빈 문자열 또는 공백으로 설정하려 할 경우
        """
        branch = Branch.objects.get(id=branch_id, deleted_at__isnull=True)

        if branch.author != author:
            raise PermissionError("브랜치 수정 권한이 없습니다.")

        allowed_fields = ["name", "description", "cover_image_url"]
        has_changes = False

        for field in allowed_fields:
            if field in data and getattr(branch, field) != data[field]:
                # Validate name is not empty/whitespace
                if field == "name" and not str(data[field]).strip():
                    raise ValueError("브랜치 이름은 필수입니다.")
                setattr(branch, field, data[field])
                has_changes = True

        if has_changes:
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
        브랜치의 공개 상태를 변경하고 관련된 소속 소설의 linked_branch_count와 브랜치 버전을 갱신한다.
        
        Parameters:
            branch_id (int): 변경할 브랜치의 PK.
            author (User): 변경을 시도하는 사용자(브랜치 소유자여야 함).
            visibility (str): 설정할 공개 상태(BranchVisibility 열거형 값 중 하나).
        
        Returns:
            Branch: 갱신된 Branch 인스턴스.
        
        Raises:
            PermissionError: author가 브랜치 소유자가 아닐 경우.
            ValueError: 메인 브랜치의 공개 상태를 변경하려 할 경우.
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