package io.forklore.dto.response;

import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.novel.NovelStatus;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
@Schema(description = "소설 목록 요약 응답")
public class NovelSummaryResponse {

    @Schema(description = "소설 ID")
    private Long id;

    @Schema(description = "소설 제목")
    private String title;

    @Schema(description = "작가 닉네임")
    private String authorNickname;

    @Schema(description = "표지 이미지 URL")
    private String coverImageUrl;

    @Schema(description = "장르")
    private Genre genre;

    @Schema(description = "연령 등급")
    private AgeRating ageRating;

    @Schema(description = "상태")
    private NovelStatus status;

    @Schema(description = "총 조회수")
    private long totalViewCount;

    @Schema(description = "총 회차 수")
    private int totalChapterCount;

    public static NovelSummaryResponse from(Novel novel) {
        return NovelSummaryResponse.builder()
                .id(novel.getId())
                .title(novel.getTitle())
                .authorNickname(novel.getAuthor().getNickname())
                .coverImageUrl(novel.getCoverImageUrl())
                .genre(novel.getGenre())
                .ageRating(novel.getAgeRating())
                .status(novel.getStatus())
                .totalViewCount(novel.getTotalViewCount())
                .totalChapterCount(novel.getTotalChapterCount())
                .build();
    }
}
