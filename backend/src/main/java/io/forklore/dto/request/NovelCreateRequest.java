package io.forklore.dto.request;

import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@Schema(description = "소설 생성 요청")
public class NovelCreateRequest {

    @NotBlank(message = "제목은 필수입니다")
    @Size(max = 200, message = "제목은 200자 이하여야 합니다")
    @Schema(description = "소설 제목", example = "흑마법사의 회귀")
    private String title;

    @Size(max = 5000, message = "설명은 5000자 이하여야 합니다")
    @Schema(description = "소설 설명")
    private String description;

    @Schema(description = "표지 이미지 URL")
    private String coverImageUrl;

    @NotNull(message = "장르는 필수입니다")
    @Schema(description = "장르", example = "FANTASY")
    private Genre genre;

    @Schema(description = "연령 등급", example = "ALL")
    private AgeRating ageRating;

    @Schema(description = "브랜치 허용 여부", example = "true")
    private Boolean allowBranching;

    @Builder
    public NovelCreateRequest(String title, String description, String coverImageUrl, Genre genre, AgeRating ageRating, Boolean allowBranching) {
        this.title = title;
        this.description = description;
        this.coverImageUrl = coverImageUrl;
        this.genre = genre;
        this.ageRating = ageRating;
        this.allowBranching = allowBranching;
    }
}
