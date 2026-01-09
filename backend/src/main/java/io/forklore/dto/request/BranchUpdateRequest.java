package io.forklore.dto.request;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Size;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@Schema(description = "브랜치 수정 요청")
public class BranchUpdateRequest {

    @Size(max = 200, message = "브랜치명은 200자 이하여야 합니다")
    @Schema(description = "브랜치명")
    private String name;

    @Size(max = 5000, message = "설명은 5000자 이하여야 합니다")
    @Schema(description = "브랜치 설명")
    private String description;

    @Schema(description = "표지 이미지 URL")
    private String coverImageUrl;

    @Builder
    public BranchUpdateRequest(String name, String description, String coverImageUrl) {
        this.name = name;
        this.description = description;
        this.coverImageUrl = coverImageUrl;
    }
}
