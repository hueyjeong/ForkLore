from django.db import models
from django.conf import settings
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


class ContributorType(models.TextChoices):
    USER = "USER", "사용자"
    AI = "AI", "AI"


class WikiTagDefinition(BaseModel):
    """위키 태그 정의"""

    branch = models.ForeignKey(
        "novels.Branch", on_delete=models.CASCADE, related_name="wiki_tag_definitions"
    )

    name = models.CharField("태그명", max_length=100)
    color = models.CharField("색상", max_length=7, blank=True)
    icon = models.CharField("아이콘", max_length=50, blank=True)
    description = models.TextField("설명", blank=True)
    display_order = models.IntegerField("정렬 순서", default=0)

    class Meta:
        db_table = "wiki_tag_definitions"
        verbose_name = "위키 태그 정의"
        verbose_name_plural = "위키 태그 정의들"
        unique_together = [["branch", "name"]]
        ordering = ["display_order", "name"]

    def __str__(self):
        return f"{self.branch.name} - {self.name}"


class WikiEntry(BaseModel):
    """위키 엔트리 (캐릭터, 장소, 아이템 등)"""

    branch = models.ForeignKey(
        "novels.Branch", on_delete=models.CASCADE, related_name="wiki_entries"
    )

    # 포크된 위키인 경우 원본 참조
    source_wiki = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="forked_wikis",
    )

    name = models.CharField("이름", max_length=200)
    image_url = models.URLField("이미지 URL", blank=True)
    first_appearance = models.IntegerField("첫 등장 회차", null=True, blank=True)
    hidden_note = models.TextField("작가 노트 (비공개)", blank=True)
    ai_metadata = models.JSONField("AI 메타데이터", null=True, blank=True)

    # M2M 태그 관계
    tags = models.ManyToManyField(
        WikiTagDefinition,
        related_name="wiki_entries",
        blank=True,
        db_table="wiki_tags",
    )

    class Meta:
        db_table = "wiki_entries"
        verbose_name = "위키 엔트리"
        verbose_name_plural = "위키 엔트리들"
        unique_together = [["branch", "name"]]
        ordering = ["name"]

    def __str__(self):
        return f"{self.branch.name} - {self.name}"


class WikiSnapshot(BaseModel):
    """위키 스냅샷 (회차별 버전)"""

    wiki_entry = models.ForeignKey(WikiEntry, on_delete=models.CASCADE, related_name="snapshots")

    content = models.TextField("내용")
    valid_from_chapter = models.IntegerField("유효 시작 회차")
    contributor_type = models.CharField(
        "기여자 유형",
        max_length=10,
        choices=ContributorType.choices,
        default=ContributorType.USER,
    )
    contributor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="wiki_contributions",
    )

    class Meta:
        db_table = "wiki_snapshots"
        verbose_name = "위키 스냅샷"
        verbose_name_plural = "위키 스냅샷들"
        unique_together = [["wiki_entry", "valid_from_chapter"]]
        ordering = ["valid_from_chapter"]

    def __str__(self):
        return f"{self.wiki_entry.name} - 회차 {self.valid_from_chapter}~"
