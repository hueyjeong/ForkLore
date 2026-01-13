from django.db import models
from common.models import BaseModel


class ChapterStatus(models.TextChoices):
    DRAFT = "DRAFT", "임시저장"
    SCHEDULED = "SCHEDULED", "예약"
    PUBLISHED = "PUBLISHED", "발행됨"


class AccessType(models.TextChoices):
    FREE = "FREE", "무료"
    SUBSCRIPTION = "SUBSCRIPTION", "구독"


class Chapter(BaseModel):
    branch = models.ForeignKey("novels.Branch", on_delete=models.CASCADE, related_name="chapters")

    chapter_number = models.IntegerField("회차 번호")
    title = models.CharField("제목", max_length=200)
    content = models.TextField("마크다운 내용")
    content_html = models.TextField("HTML 내용", blank=True)
    word_count = models.IntegerField("글자 수", default=0)

    status = models.CharField(
        "상태", max_length=20, choices=ChapterStatus.choices, default=ChapterStatus.DRAFT
    )
    access_type = models.CharField(
        "접근 타입", max_length=20, choices=AccessType.choices, default=AccessType.FREE
    )
    price = models.IntegerField("가격", default=0)

    scheduled_at = models.DateTimeField("예약 시간", null=True, blank=True)
    published_at = models.DateTimeField("발행 시간", null=True, blank=True)

    view_count = models.BigIntegerField("조회수", default=0)
    like_count = models.BigIntegerField("좋아요 수", default=0)
    comment_count = models.IntegerField("댓글 수", default=0)

    class Meta:
        db_table = "chapters"
        verbose_name = "회차"
        verbose_name_plural = "회차들"
        unique_together = ["branch", "chapter_number"]
        ordering = ["chapter_number"]

    def __str__(self):
        return f"{self.branch.name} - {self.chapter_number}화: {self.title}"
