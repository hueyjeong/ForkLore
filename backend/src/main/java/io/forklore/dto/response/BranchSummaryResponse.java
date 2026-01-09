package io.forklore.dto.response;

import io.forklore.domain.branch.Branch;
import io.forklore.domain.branch.BranchType;
import io.forklore.domain.branch.BranchVisibility;
import io.forklore.domain.branch.CanonStatus;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "브랜치 목록 요약 응답")
public class BranchSummaryResponse {

    @Schema(description = "브랜치 ID")
    private Long id;

    @Schema(description = "브랜치명")
    private String name;

    @Schema(description = "작가 닉네임")
    private String authorNickname;

    @Schema(description = "표지 이미지 URL")
    private String coverImageUrl;

    @Schema(description = "브랜치 타입")
    private BranchType branchType;

    @Schema(description = "가시성")
    private BranchVisibility visibility;

    @Schema(description = "정사 편입 상태")
    private CanonStatus canonStatus;

    @Schema(description = "투표 수")
    private long voteCount;

    @Schema(description = "회차 수")
    private int chapterCount;

    @Schema(description = "메인 브랜치 여부")
    private boolean isMain;

    public static BranchSummaryResponse from(Branch branch) {
        return BranchSummaryResponse.builder()
                .id(branch.getId())
                .name(branch.getName())
                .authorNickname(branch.getAuthor().getNickname())
                .coverImageUrl(branch.getCoverImageUrl())
                .branchType(branch.getBranchType())
                .visibility(branch.getVisibility())
                .canonStatus(branch.getCanonStatus())
                .voteCount(branch.getVoteCount())
                .chapterCount(branch.getChapterCount())
                .isMain(branch.isMain())
                .build();
    }
}
