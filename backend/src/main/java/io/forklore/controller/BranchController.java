package io.forklore.controller;

import io.forklore.domain.branch.BranchVisibility;
import io.forklore.dto.request.BranchCreateRequest;
import io.forklore.dto.request.BranchUpdateRequest;
import io.forklore.dto.request.LinkRequestCreateRequest;
import io.forklore.dto.response.BranchResponse;
import io.forklore.dto.response.BranchSummaryResponse;
import io.forklore.dto.response.LinkRequestResponse;
import io.forklore.global.common.ApiResponse;
import io.forklore.security.UserPrincipal;
import io.forklore.service.branch.BranchLinkService;
import io.forklore.service.branch.BranchService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@Tag(name = "Branch", description = "브랜치 관리 API")
public class BranchController {

    private final BranchService branchService;
    private final BranchLinkService branchLinkService;

    // ==================== 소설 하위 브랜치 API ====================

    @GetMapping("/novels/{novelId}/branches")
    @Operation(summary = "브랜치 목록 조회", description = "소설의 공개 브랜치 목록을 조회합니다.")
    public ApiResponse<Page<BranchSummaryResponse>> getBranchList(
            @PathVariable Long novelId,
            @PageableDefault(size = 20) Pageable pageable) {
        Page<BranchSummaryResponse> response = branchService.getPublicBranchList(novelId, pageable);
        return ApiResponse.success(response);
    }

    @PostMapping("/novels/{novelId}/branches")
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "브랜치 포크", description = "소설에서 새로운 브랜치를 생성합니다.")
    public ApiResponse<BranchResponse> fork(
            @PathVariable Long novelId,
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @Valid @RequestBody BranchCreateRequest request) {
        BranchResponse response = branchService.fork(novelId, userPrincipal.getId(), request);
        return ApiResponse.success(response, "브랜치가 생성되었습니다.");
    }

    @GetMapping("/novels/{novelId}/branches/main")
    @Operation(summary = "메인 브랜치 조회", description = "소설의 메인 브랜치를 조회합니다.")
    public ApiResponse<BranchResponse> getMainBranch(@PathVariable Long novelId) {
        BranchResponse response = branchService.getMainBranch(novelId);
        return ApiResponse.success(response);
    }

    // ==================== 브랜치 직접 API ====================

    @GetMapping("/branches/{id}")
    @Operation(summary = "브랜치 상세 조회", description = "브랜치 상세 정보를 조회합니다.")
    public ApiResponse<BranchResponse> getDetail(@PathVariable Long id) {
        BranchResponse response = branchService.getDetail(id);
        return ApiResponse.success(response);
    }

    @PatchMapping("/branches/{id}")
    @Operation(summary = "브랜치 수정", description = "브랜치 정보를 수정합니다. 작가 본인만 가능합니다.")
    public ApiResponse<BranchResponse> update(
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @PathVariable Long id,
            @Valid @RequestBody BranchUpdateRequest request) {
        BranchResponse response = branchService.update(userPrincipal.getId(), id, request);
        return ApiResponse.success(response, "브랜치가 수정되었습니다.");
    }

    @DeleteMapping("/branches/{id}")
    @Operation(summary = "브랜치 삭제", description = "브랜치를 삭제합니다. 작가 본인만 가능합니다.")
    public ApiResponse<Void> delete(
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @PathVariable Long id) {
        branchService.delete(userPrincipal.getId(), id);
        return ApiResponse.success();
    }

    @PatchMapping("/branches/{id}/visibility")
    @Operation(summary = "가시성 변경", description = "브랜치 가시성을 변경합니다.")
    public ApiResponse<BranchResponse> changeVisibility(
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @PathVariable Long id,
            @RequestParam BranchVisibility visibility) {
        BranchResponse response = branchService.changeVisibility(userPrincipal.getId(), id, visibility);
        return ApiResponse.success(response, "가시성이 변경되었습니다.");
    }

    // ==================== 투표 API ====================

    @PostMapping("/branches/{id}/vote")
    @Operation(summary = "브랜치 투표", description = "브랜치에 투표합니다.")
    public ApiResponse<Void> vote(
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @PathVariable Long id) {
        branchService.vote(userPrincipal.getId(), id);
        return ApiResponse.success(null, "투표가 완료되었습니다.");
    }

    @DeleteMapping("/branches/{id}/vote")
    @Operation(summary = "투표 취소", description = "브랜치 투표를 취소합니다.")
    public ApiResponse<Void> unvote(
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @PathVariable Long id) {
        branchService.unvote(userPrincipal.getId(), id);
        return ApiResponse.success(null, "투표가 취소되었습니다.");
    }

    // ==================== 연결 요청 API ====================

    @PostMapping("/branches/{id}/link-request")
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "연결 요청 생성", description = "브랜치를 원작 소설 페이지에 연결 요청합니다.")
    public ApiResponse<LinkRequestResponse> requestLink(
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @PathVariable Long id,
            @Valid @RequestBody LinkRequestCreateRequest request) {
        LinkRequestResponse response = branchLinkService.requestLink(id, userPrincipal.getId(), request.getRequestMessage());
        return ApiResponse.success(response, "연결 요청이 생성되었습니다.");
    }

    @PostMapping("/link-requests/{requestId}/approve")
    @Operation(summary = "연결 요청 승인", description = "연결 요청을 승인합니다. 원작 작가만 가능합니다.")
    public ApiResponse<LinkRequestResponse> approveLink(
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @PathVariable Long requestId,
            @RequestParam(required = false) String comment) {
        LinkRequestResponse response = branchLinkService.approveLink(requestId, userPrincipal.getId(), comment);
        return ApiResponse.success(response, "연결 요청이 승인되었습니다.");
    }

    @PostMapping("/link-requests/{requestId}/reject")
    @Operation(summary = "연결 요청 거절", description = "연결 요청을 거절합니다. 원작 작가만 가능합니다.")
    public ApiResponse<LinkRequestResponse> rejectLink(
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @PathVariable Long requestId,
            @RequestParam(required = false) String comment) {
        LinkRequestResponse response = branchLinkService.rejectLink(requestId, userPrincipal.getId(), comment);
        return ApiResponse.success(response, "연결 요청이 거절되었습니다.");
    }
}
