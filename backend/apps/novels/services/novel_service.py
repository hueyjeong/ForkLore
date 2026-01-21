from django.db import transaction
from django.db.models import QuerySet

from apps.users.models import User

from ..models import (
    AgeRating,
    Branch,
    BranchType,
    BranchVisibility,
    Genre,
    Novel,
    NovelStatus,
)


class NovelService:
    """Service class for Novel-related business logic."""

    @transaction.atomic
    def create(self, author: User, data: dict) -> Novel:
        """
        새 소설을 생성하고 해당 소설의 메인 분기(Branch)를 자동으로 생성합니다.
        
        Parameters:
            author (User): 소설을 생성하는 작성자.
            data (dict): 소설 속성들을 담은 사전(예: "title", "description", "genre", "age_rating", "status", "cover_image_url", "allow_branching").
        
        Returns:
            Novel: 생성된 Novel 인스턴스.
        
        Raises:
            ValueError: "title"이 없거나 빈 문자열인 경우.
        """
        # Validate required fields - strip and check for empty
        raw_title = data.get("title")
        title = str(raw_title).strip() if raw_title is not None else ""
        if not title:
            raise ValueError("제목은 필수입니다.")

        novel = Novel.objects.create(
            author=author,
            title=title,
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
        지운(novel.deleted_at이 설정된) 소설을 제외하고 필터와 정렬을 적용하여 소설 목록을 반환합니다.
        
        Parameters:
            filters (dict | None): 적용 가능한 키: `genre`, `status`, `author`, `age_rating`. 각 키가 존재하면 해당 값으로 필터합니다.
            sort (str | None): 정렬 기준. `"popular"`(조회수 내림), `"likes"`(좋아요 수 내림), 그 외 또는 `None`은 생성일 내림(최신).
        
        Returns:
            QuerySet[Novel]: 필터와 정렬이 적용된 소설 쿼리셋(soft-deleted된 항목 제외).
        """
        queryset = Novel.objects.filter(deleted_at__isnull=True).select_related("author")

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
        주어진 ID에 해당하는 삭제되지 않은 소설을 조회합니다.
        
        Parameters:
            novel_id (int): 조회할 소설의 기본 키
        
        Returns:
            Novel: 조회된 Novel 인스턴스
        
        Raises:
            Novel.DoesNotExist: 해당 ID의 소설이 존재하지 않거나 이미 삭제된 경우
        """
        return Novel.objects.get(id=novel_id, deleted_at__isnull=True)

    @transaction.atomic
    def update(self, novel_id: int, author: User, data: dict) -> Novel:
        """
        지정된 소설의 허용된 필드를 갱신하고 저장합니다.
        
        Parameters:
            novel_id (int): 갱신할 소설의 기본 키.
            author (User): 요청한 사용자(권한 확인에 사용).
            data (dict): 갱신할 필드를 포함한 딕셔너리. 허용되는 키:
                - "title": 소설 제목(빈 문자열이 될 수 없음).
                - "description": 설명 문자열.
                - "cover_image_url": 표지 이미지 URL.
                - "genre": Genre 열거형 값.
                - "age_rating": AgeRating 열거형 값.
                - "status": NovelStatus 열거형 값.
                - "allow_branching": 분기 허용 여부(boolean).
        
        Returns:
            Novel: 갱신되어 저장된 Novel 인스턴스.
        
        Raises:
            Novel.DoesNotExist: 지정한 ID의 소설을 찾을 수 없거나 삭제된 경우.
            PermissionError: 요청한 사용자가 소설의 작성자가 아닌 경우.
            ValueError: 제공된 제목이 빈 문자열인 경우.
        """
        novel = Novel.objects.get(id=novel_id, deleted_at__isnull=True)

        if novel.author != author:
            raise PermissionError("소설 수정 권한이 없습니다.")

        # Validate title if provided - strip and normalize
        if "title" in data:
            title = str(data["title"]).strip()
            if not title:
                raise ValueError("제목은 필수입니다.")
            data["title"] = title

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
    def delete(self, novel_id: int, author: User) -> None:
        """
        지정된 소설을 소프트 삭제한다.
        
        Parameters:
            novel_id (int): 삭제할 소설의 기본키.
            author (User): 삭제를 시도하는 사용자(소설의 저자여야 함).
        
        Raises:
            Novel.DoesNotExist: 해당 ID의 소설이 없거나 이미 삭제된 경우.
            PermissionError: 요청 사용자가 소설의 저자가 아닌 경우.
        """
        novel = Novel.objects.get(id=novel_id, deleted_at__isnull=True)

        if novel.author != author:
            raise PermissionError("소설 삭제 권한이 없습니다.")

        novel.soft_delete()