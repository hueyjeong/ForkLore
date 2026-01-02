package io.forklore.dto.request;

import io.forklore.domain.branch.BranchType;
import io.forklore.domain.branch.BranchVisibility;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@Schema(description = "브랜치 생성/포크 요청")
public class BranchCreateRequest {

    @Schema(description = "부모 브랜치 ID (포크 시)")
    private Long parentBranchId;

    @Schema(description = "분기점 회차 번호 (포크 시)")
    private Integer forkPointChapter;

    @NotBlank(message = "브랜치명은 필수입니다")
    @Size(max = 200, message = "브랜치명은 200자 이하여야 합니다")
    @Schema(description = "브랜치명", example = "IF: 만약 주인공이...")
    private String name;

    @Size(max = 5000, message = "설명은 5000자 이하여야 합니다")
    @Schema(description = "브랜치 설명")
    private String description;

    @Schema(description = "표지 이미지 URL")
    private String coverImageUrl;

    @Schema(description = "브랜치 타입", example = "IF_STORY")
    private BranchType branchType;

    @Schema(description = "가시성", example = "PRIVATE")
    private BranchVisibility visibility;

    @Builder
    public BranchCreateRequest(Long parentBranchId, Integer forkPointChapter, String name,
                               String description, String coverImageUrl, BranchType branchType,
                               BranchVisibility visibility) {
        this.parentBranchId = parentBranchId;
        this.forkPointChapter = forkPointChapter;
        this.name = name;
        this.description = description;
        this.coverImageUrl = coverImageUrl;
        this.branchType = branchType;
        this.visibility = visibility;
    }
}
