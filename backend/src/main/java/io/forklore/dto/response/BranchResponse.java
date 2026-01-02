package io.forklore.dto.response;

import io.forklore.domain.branch.*;
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
@Schema(description = "브랜치 상세 응답")
public class BranchResponse {

    @Schema(description = "브랜치 ID")
    private Long id;

    @Schema(description = "소설 ID")
    private Long novelId;

    @Schema(description = "소설 제목")
    private String novelTitle;

    @Schema(description = "작가 정보")
    private AuthorInfo author;

    @Schema(description = "메인 브랜치 여부")
    private boolean isMain;

    @Schema(description = "부모 브랜치 ID")
    private Long parentBranchId;

    @Schema(description = "분기점 회차 번호")
    private Integer forkPointChapter;

    @Schema(description = "브랜치명")
    private String name;

    @Schema(description = "설명")
    private String description;

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

    @Schema(description = "조회 수")
    private long viewCount;

    @Schema(description = "회차 수")
    private int chapterCount;

    @Schema(description = "생성일")
    private LocalDateTime createdAt;

    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AuthorInfo {
        private Long id;
        private String nickname;
        private String profileImageUrl;
    }

    public static BranchResponse from(Branch branch) {
        return BranchResponse.builder()
                .id(branch.getId())
                .novelId(branch.getNovel().getId())
                .novelTitle(branch.getNovel().getTitle())
                .author(AuthorInfo.builder()
                        .id(branch.getAuthor().getId())
                        .nickname(branch.getAuthor().getNickname())
                        .profileImageUrl(branch.getAuthor().getProfileImageUrl())
                        .build())
                .isMain(branch.isMain())
                .parentBranchId(branch.getParentBranch() != null ? branch.getParentBranch().getId() : null)
                .forkPointChapter(branch.getForkPointChapter())
                .name(branch.getName())
                .description(branch.getDescription())
                .coverImageUrl(branch.getCoverImageUrl())
                .branchType(branch.getBranchType())
                .visibility(branch.getVisibility())
                .canonStatus(branch.getCanonStatus())
                .voteCount(branch.getVoteCount())
                .viewCount(branch.getViewCount())
                .chapterCount(branch.getChapterCount())
                .createdAt(branch.getCreatedAt())
                .build();
    }
}
