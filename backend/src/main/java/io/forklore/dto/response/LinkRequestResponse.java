package io.forklore.dto.response;

import io.forklore.domain.branch.BranchLinkRequest;
import io.forklore.domain.branch.LinkRequestStatus;
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
@Schema(description = "연결 요청 응답")
public class LinkRequestResponse {

    @Schema(description = "요청 ID")
    private Long id;

    @Schema(description = "브랜치 ID")
    private Long branchId;

    @Schema(description = "브랜치명")
    private String branchName;

    @Schema(description = "상태")
    private LinkRequestStatus status;

    @Schema(description = "요청 메시지")
    private String requestMessage;

    @Schema(description = "리뷰어 닉네임")
    private String reviewerNickname;

    @Schema(description = "리뷰 코멘트")
    private String reviewComment;

    @Schema(description = "리뷰 일시")
    private LocalDateTime reviewedAt;

    @Schema(description = "생성일")
    private LocalDateTime createdAt;

    public static LinkRequestResponse from(BranchLinkRequest request) {
        return LinkRequestResponse.builder()
                .id(request.getId())
                .branchId(request.getBranch().getId())
                .branchName(request.getBranch().getName())
                .status(request.getStatus())
                .requestMessage(request.getRequestMessage())
                .reviewerNickname(request.getReviewer() != null ? request.getReviewer().getNickname() : null)
                .reviewComment(request.getReviewComment())
                .reviewedAt(request.getReviewedAt())
                .createdAt(request.getCreatedAt())
                .build();
    }
}
