package io.forklore.dto.request;

import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.NovelStatus;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Size;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@Schema(description = "소설 수정 요청")
public class NovelUpdateRequest {

    @Size(max = 200, message = "제목은 200자 이하여야 합니다")
    @Schema(description = "소설 제목")
    private String title;

    @Size(max = 5000, message = "설명은 5000자 이하여야 합니다")
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
    private Boolean allowBranching;

    @Builder
    public NovelUpdateRequest(String title, String description, String coverImageUrl, Genre genre, AgeRating ageRating, NovelStatus status, Boolean allowBranching) {
        this.title = title;
        this.description = description;
        this.coverImageUrl = coverImageUrl;
        this.genre = genre;
        this.ageRating = ageRating;
        this.status = status;
        this.allowBranching = allowBranching;
    }
}
