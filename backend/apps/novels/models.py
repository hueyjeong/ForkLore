from django.conf import settings
from django.db import models

from common.models import BaseModel, SoftDeleteModel


class Genre(models.TextChoices):
    FANTASY = "FANTASY", "판타지"
    ROMANCE = "ROMANCE", "로맨스"
    ACTION = "ACTION", "액션"
    THRILLER = "THRILLER", "스릴러"
    MYSTERY = "MYSTERY", "미스터리"
    SF = "SF", "SF"
    HISTORY = "HISTORY", "대체역사"
    MODERN = "MODERN", "현대"
    MARTIAL = "MARTIAL", "무협"
    GAME = "GAME", "게임"


class AgeRating(models.TextChoices):
    ALL = "ALL", "전체"
    AGE_12 = "12", "12세"
    AGE_15 = "15", "15세"
    AGE_19 = "19", "19세"


class NovelStatus(models.TextChoices):
    ONGOING = "ONGOING", "연재중"
    COMPLETED = "COMPLETED", "완결"
    HIATUS = "HIATUS", "휴재"


class Novel(SoftDeleteModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="novels"
    )
    title = models.CharField("제목", max_length=200)
    description = models.TextField("설명", blank=True)
    cover_image_url = models.URLField("표지", blank=True)

    genre = models.CharField("장르", max_length=50, choices=Genre.choices)
    age_rating = models.CharField(
        "연령등급", max_length=10, choices=AgeRating.choices, default=AgeRating.ALL
    )
    status = models.CharField(
        "상태", max_length=20, choices=NovelStatus.choices, default=NovelStatus.ONGOING
    )

    allow_branching = models.BooleanField("브랜치 허용", default=True)
    is_exclusive = models.BooleanField("독점작", default=False)
    is_premium = models.BooleanField("프리미엄", default=False)

    total_view_count = models.BigIntegerField("총 조회수", default=0)
    total_like_count = models.BigIntegerField("총 좋아요", default=0)
    total_chapter_count = models.IntegerField("총 회차 수", default=0)
    branch_count = models.IntegerField("브랜치 수", default=1)
    linked_branch_count = models.IntegerField("연결된 브랜치 수", default=0)

    class Meta:
        db_table = "novels"
        verbose_name = "소설"
        verbose_name_plural = "소설들"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class BranchType(models.TextChoices):
    MAIN = "MAIN", "메인"
    SIDE_STORY = "SIDE_STORY", "외전"
    FAN_FIC = "FAN_FIC", "팬픽"
    IF_STORY = "IF_STORY", "IF 스토리"


class BranchVisibility(models.TextChoices):
    PRIVATE = "PRIVATE", "비공개"
    PUBLIC = "PUBLIC", "공개"
    LINKED = "LINKED", "연결됨"


class CanonStatus(models.TextChoices):
    NON_CANON = "NON_CANON", "비정사"
    CANDIDATE = "CANDIDATE", "후보"
    MERGED = "MERGED", "편입됨"


class Branch(SoftDeleteModel):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name="branches")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="branches"
    )

    is_main = models.BooleanField("메인 브랜치", default=False)
    parent_branch = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="child_branches"
    )
    fork_point_chapter = models.IntegerField("분기 회차", null=True, blank=True)

    name = models.CharField("이름", max_length=200)
    description = models.TextField("설명", blank=True)
    cover_image_url = models.URLField("표지", blank=True)

    branch_type = models.CharField(
        "브랜치 타입", max_length=20, choices=BranchType.choices, default=BranchType.FAN_FIC
    )
    visibility = models.CharField(
        "공개 상태",
        max_length=20,
        choices=BranchVisibility.choices,
        default=BranchVisibility.PRIVATE,
    )
    canon_status = models.CharField(
        "정사 상태", max_length=20, choices=CanonStatus.choices, default=CanonStatus.NON_CANON
    )
    merged_at_chapter = models.IntegerField("편입 회차", null=True, blank=True)

    vote_count = models.BigIntegerField("투표 수", default=0)
    vote_threshold = models.IntegerField("투표 임계값", default=1000)
    view_count = models.BigIntegerField("조회수", default=0)
    chapter_count = models.IntegerField("회차 수", default=0)

    class Meta:
        db_table = "branches"
        verbose_name = "브랜치"
        verbose_name_plural = "브랜치들"
        constraints = [
            models.UniqueConstraint(
                fields=["novel"],
                condition=models.Q(is_main=True),
                name="unique_main_branch_per_novel",
            )
        ]

    def __str__(self) -> str:
        return f"{self.novel.title} - {self.name}"


class BranchVote(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="branch_votes"
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="votes")

    class Meta:
        db_table = "branch_votes"
        unique_together = ["user", "branch"]


class LinkRequestStatus(models.TextChoices):
    PENDING = "PENDING", "대기중"
    APPROVED = "APPROVED", "승인됨"
    REJECTED = "REJECTED", "거절됨"


class BranchLinkRequest(BaseModel):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="link_requests")
    status = models.CharField(
        "상태", max_length=20, choices=LinkRequestStatus.choices, default=LinkRequestStatus.PENDING
    )
    request_message = models.TextField("요청 메시지", blank=True)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_link_requests",
    )
    review_comment = models.TextField("리뷰 코멘트", blank=True)
    reviewed_at = models.DateTimeField("리뷰 일시", null=True, blank=True)

    class Meta:
        db_table = "branch_link_requests"
        verbose_name = "브랜치 연결 요청"
        verbose_name_plural = "브랜치 연결 요청들"
