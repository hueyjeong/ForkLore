package io.forklore.dto.response;

import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.novel.NovelStatus;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.time.LocalDateTime;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "소설 상세 응답")
public class NovelResponse {

    @Schema(description = "소설 ID")
    private Long id;

    @Schema(description = "작가 정보")
    private AuthorInfo author;

    @Schema(description = "소설 제목")
    private String title;

    @Schema(description = "소설 설명")
    private String description;

    @Schema(description = "표지 이미지 URL")
    private String coverImageUrl;

    @Schema(description = "장르")
    private Genre genre;

    @Schema(description = "연령 등급")
    private AgeRating ageRating;

    @Schema(description = "상태")
    private NovelStatus status;

    @Schema(description = "브랜치 허용 여부")
    private boolean allowBranching;

    @Schema(description = "총 조회수")
    private long totalViewCount;

    @Schema(description = "총 좋아요 수")
    private long totalLikeCount;

    @Schema(description = "총 회차 수")
    private int totalChapterCount;

    @Schema(description = "브랜치 수")
    private int branchCount;

    @Schema(description = "생성일")
    private LocalDateTime createdAt;

    @Schema(description = "수정일")
    private LocalDateTime updatedAt;

    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AuthorInfo {
        private Long id;
        private String nickname;
        private String profileImageUrl;
    }

    public static NovelResponse from(Novel novel) {
        return NovelResponse.builder()
                .id(novel.getId())
                .author(AuthorInfo.builder()
                        .id(novel.getAuthor().getId())
                        .nickname(novel.getAuthor().getNickname())
                        .profileImageUrl(novel.getAuthor().getProfileImageUrl())
                        .build())
                .title(novel.getTitle())
                .description(novel.getDescription())
                .coverImageUrl(novel.getCoverImageUrl())
                .genre(novel.getGenre())
                .ageRating(novel.getAgeRating())
                .status(novel.getStatus())
                .allowBranching(novel.isAllowBranching())
                .totalViewCount(novel.getTotalViewCount())
                .totalLikeCount(novel.getTotalLikeCount())
                .totalChapterCount(novel.getTotalChapterCount())
                .branchCount(novel.getBranchCount())
                .createdAt(novel.getCreatedAt())
                .updatedAt(novel.getUpdatedAt())
                .build();
    }
}
