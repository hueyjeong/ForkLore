from django.db import models
from django.conf import settings
from common.models import BaseModel, SoftDeleteModel


class PlanType(models.TextChoices):
    BASIC = "BASIC", "베이직"
    PREMIUM = "PREMIUM", "프리미엄"


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "활성"
    CANCELLED = "CANCELLED", "취소됨"
    EXPIRED = "EXPIRED", "만료됨"


class Subscription(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan_type = models.CharField("플랜 타입", max_length=20, choices=PlanType.choices)
    started_at = models.DateTimeField("시작일", auto_now_add=True)
    expires_at = models.DateTimeField("만료일")
    payment_id = models.CharField("결제 ID", max_length=255, blank=True)
    auto_renew = models.BooleanField("자동 갱신", default=True)
    status = models.CharField(
        "상태", max_length=20, choices=SubscriptionStatus.choices, default=SubscriptionStatus.ACTIVE
    )
    cancelled_at = models.DateTimeField("취소일", null=True, blank=True)

    class Meta:
        db_table = "subscriptions"
        verbose_name = "구독"
        verbose_name_plural = "구독들"


class Purchase(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="purchases"
    )
    chapter = models.ForeignKey(
        "contents.Chapter", on_delete=models.CASCADE, related_name="purchases"
    )
    price_paid = models.IntegerField("결제 금액")

    class Meta:
        db_table = "purchases"
        verbose_name = "소장"
        verbose_name_plural = "소장 목록"
        unique_together = ["user", "chapter"]


class ReadingLog(SoftDeleteModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reading_logs"
    )
    chapter = models.ForeignKey(
        "contents.Chapter", on_delete=models.CASCADE, related_name="reading_logs"
    )
    progress = models.DecimalField("진행률", max_digits=5, decimal_places=4, default=0)
    is_completed = models.BooleanField("완독 여부", default=False)
    read_at = models.DateTimeField("읽은 시간", auto_now=True)

    class Meta:
        db_table = "reading_logs"
        verbose_name = "읽은 기록"
        verbose_name_plural = "읽은 기록들"
        unique_together = ["user", "chapter"]


class Bookmark(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks"
    )
    chapter = models.ForeignKey(
        "contents.Chapter", on_delete=models.CASCADE, related_name="bookmarks"
    )
    scroll_position = models.DecimalField("스크롤 위치", max_digits=5, decimal_places=4, default=0)
    note = models.CharField("메모", max_length=500, blank=True)

    class Meta:
        db_table = "bookmarks"
        verbose_name = "책갈피"
        verbose_name_plural = "책갈피들"
        unique_together = ["user", "chapter"]


class Comment(SoftDeleteModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    chapter = models.ForeignKey(
        "contents.Chapter", on_delete=models.CASCADE, related_name="comments"
    )
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    content = models.TextField("내용")
    is_spoiler = models.BooleanField("스포일러 여부", default=False)
    is_pinned = models.BooleanField("고정 여부", default=False)
    like_count = models.IntegerField("좋아요 수", default=0)

    # Paragraph comment fields
    paragraph_index = models.IntegerField("문단 인덱스", null=True, blank=True)
    selection_start = models.IntegerField("선택 시작", null=True, blank=True)
    selection_end = models.IntegerField("선택 끝", null=True, blank=True)
    quoted_text = models.TextField("인용 텍스트", blank=True)

    class Meta:
        db_table = "comments"
        verbose_name = "댓글"
        verbose_name_plural = "댓글들"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["chapter", "paragraph_index"]),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.selection_start is not None and self.selection_end is not None:
            if self.selection_start >= self.selection_end:
                raise ValidationError("selection_start must be less than selection_end")


class Like(BaseModel):
    """Like model with GenericForeignKey for polymorphic likes."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    # Generic relation fields
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    class Meta:
        db_table = "likes"
        verbose_name = "좋아요"
        verbose_name_plural = "좋아요들"
        unique_together = ["user", "content_type", "object_id"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class ReportReason(models.TextChoices):
    """Reasons for reporting content."""

    SPAM = "SPAM", "스팸"
    ABUSE = "ABUSE", "욕설/비방"
    SPOILER = "SPOILER", "스포일러"
    COPYRIGHT = "COPYRIGHT", "저작권 침해"
    OTHER = "OTHER", "기타"


class ReportStatus(models.TextChoices):
    """Status of a report."""

    PENDING = "PENDING", "대기중"
    RESOLVED = "RESOLVED", "처리완료"
    REJECTED = "REJECTED", "반려"


class Report(BaseModel):
    """Report model with GenericForeignKey for polymorphic reports."""

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports_submitted"
    )
    # Generic relation fields (polymorphic target)
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    reason = models.CharField("신고 사유", max_length=20, choices=ReportReason.choices)
    description = models.TextField("상세 설명", blank=True)
    status = models.CharField(
        "상태", max_length=20, choices=ReportStatus.choices, default=ReportStatus.PENDING
    )

    # Resolution fields
    resolver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports_resolved",
    )
    resolved_at = models.DateTimeField("처리일", null=True, blank=True)
    resolution_note = models.TextField("처리 메모", blank=True)

    class Meta:
        db_table = "reports"
        verbose_name = "신고"
        verbose_name_plural = "신고들"
        unique_together = ["reporter", "content_type", "object_id"]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["status"]),
        ]
