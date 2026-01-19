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
    def update(self, novel_id: int, author: User, data: dict) -> Novel:
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
    def delete(self, novel_id: int, author: User) -> None:
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
