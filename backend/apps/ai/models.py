from django.db import models
from common.models import BaseModel

try:
    from pgvector.django import VectorField
except ImportError:
    VectorField = None


class ChapterChunk(BaseModel):
    chapter = models.ForeignKey("contents.Chapter", on_delete=models.CASCADE, related_name="chunks")
    chunk_index = models.IntegerField("청크 인덱스")
    content = models.TextField("내용")

    if VectorField:
        embedding = VectorField(dimensions=3072, null=True, blank=True)
    else:
        embedding = models.BinaryField("임베딩", null=True, blank=True)

    class Meta:
        db_table = "chapter_chunks"
        verbose_name = "회차 청크"
        verbose_name_plural = "회차 청크들"
        unique_together = ["chapter", "chunk_index"]
