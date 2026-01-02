package io.forklore.dto.response;

import io.forklore.domain.chapter.AccessType;
import io.forklore.domain.chapter.Chapter;
import io.forklore.domain.chapter.ChapterStatus;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "회차 목차 요약 응답")
public class ChapterSummaryResponse {

    @Schema(description = "회차 ID")
    private Long id;

    @Schema(description = "회차 번호")
    private int chapterNumber;

    @Schema(description = "제목")
    private String title;

    @Schema(description = "글자 수")
    private int wordCount;

    @Schema(description = "상태")
    private ChapterStatus status;

    @Schema(description = "접근 타입")
    private AccessType accessType;

    @Schema(description = "가격")
    private int price;

    @Schema(description = "발행일")
    private LocalDateTime publishedAt;

    @Schema(description = "조회수")
    private long viewCount;

    @Schema(description = "좋아요 수")
    private long likeCount;

    public static ChapterSummaryResponse from(Chapter chapter) {
        return ChapterSummaryResponse.builder()
                .id(chapter.getId())
                .chapterNumber(chapter.getChapterNumber())
                .title(chapter.getTitle())
                .wordCount(chapter.getWordCount())
                .status(chapter.getStatus())
                .accessType(chapter.getAccessType())
                .price(chapter.getPrice())
                .publishedAt(chapter.getPublishedAt())
                .viewCount(chapter.getViewCount())
                .likeCount(chapter.getLikeCount())
                .build();
    }
}
