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
@Schema(description = "회차 상세 응답")
public class ChapterResponse {

    @Schema(description = "회차 ID")
    private Long id;

    @Schema(description = "브랜치 ID")
    private Long branchId;

    @Schema(description = "회차 번호")
    private int chapterNumber;

    @Schema(description = "제목")
    private String title;

    @Schema(description = "본문 (마크다운)")
    private String content;

    @Schema(description = "본문 (HTML)")
    private String contentHtml;

    @Schema(description = "글자 수")
    private int wordCount;

    @Schema(description = "상태")
    private ChapterStatus status;

    @Schema(description = "접근 타입")
    private AccessType accessType;

    @Schema(description = "가격")
    private int price;

    @Schema(description = "작가의 말")
    private String authorComment;

    @Schema(description = "예약 발행 시간")
    private LocalDateTime scheduledAt;

    @Schema(description = "발행 시간")
    private LocalDateTime publishedAt;

    @Schema(description = "조회수")
    private long viewCount;

    @Schema(description = "좋아요 수")
    private long likeCount;

    @Schema(description = "댓글 수")
    private int commentCount;

    @Schema(description = "생성일")
    private LocalDateTime createdAt;

    public static ChapterResponse from(Chapter chapter) {
        return ChapterResponse.builder()
                .id(chapter.getId())
                .branchId(chapter.getBranch().getId())
                .chapterNumber(chapter.getChapterNumber())
                .title(chapter.getTitle())
                .content(chapter.getContent())
                .contentHtml(chapter.getContentHtml())
                .wordCount(chapter.getWordCount())
                .status(chapter.getStatus())
                .accessType(chapter.getAccessType())
                .price(chapter.getPrice())
                .authorComment(chapter.getAuthorComment())
                .scheduledAt(chapter.getScheduledAt())
                .publishedAt(chapter.getPublishedAt())
                .viewCount(chapter.getViewCount())
                .likeCount(chapter.getLikeCount())
                .commentCount(chapter.getCommentCount())
                .createdAt(chapter.getCreatedAt())
                .build();
    }
}
