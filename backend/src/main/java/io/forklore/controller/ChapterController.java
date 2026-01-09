package io.forklore.controller;

import io.forklore.dto.request.ChapterCreateRequest;
import io.forklore.dto.request.ChapterUpdateRequest;
import io.forklore.dto.response.ChapterResponse;
import io.forklore.dto.response.ChapterSummaryResponse;
import io.forklore.global.common.ApiResponse;
import io.forklore.security.UserPrincipal;
import io.forklore.service.chapter.ChapterService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequiredArgsConstructor
@Tag(name = "Chapter", description = "회차 관리 API")
public class ChapterController {

    private final ChapterService chapterService;

    // ==================== 브랜치 하위 회차 API ====================

    @GetMapping("/branches/{branchId}/chapters")
    @Operation(summary = "회차 목록 조회", description = "브랜치의 회차 목록(목차)을 조회합니다.")
    public ApiResponse<List<ChapterSummaryResponse>> getChapterList(
            @PathVariable Long branchId,
            @RequestParam(defaultValue = "true") boolean publishedOnly) {
        List<ChapterSummaryResponse> response = chapterService.getList(branchId, publishedOnly);
        return ApiResponse.success(response);
    }

    @PostMapping("/branches/{branchId}/chapters")
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "회차 작성", description = "새로운 회차를 작성합니다. 초안 상태로 생성됩니다.")
    public ApiResponse<ChapterResponse> create(
            @PathVariable Long branchId,
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @Valid @RequestBody ChapterCreateRequest request) {
        ChapterResponse response = chapterService.create(branchId, userPrincipal.getId(), request);
        return ApiResponse.success(response, "회차가 작성되었습니다.");
    }

    // ==================== 회차 직접 API ====================

    @GetMapping("/chapters/{id}")
    @Operation(summary = "회차 상세 조회", description = "회차 상세 내용을 조회합니다.")
    public ApiResponse<ChapterResponse> getDetail(@PathVariable Long id) {
        ChapterResponse response = chapterService.getDetailWithViewCount(id);
        return ApiResponse.success(response);
    }

    @PatchMapping("/chapters/{id}")
    @Operation(summary = "회차 수정", description = "회차 내용을 수정합니다.")
    public ApiResponse<ChapterResponse> update(
            @PathVariable Long id,
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @Valid @RequestBody ChapterUpdateRequest request) {
        ChapterResponse response = chapterService.update(id, userPrincipal.getId(), request);
        return ApiResponse.success(response, "회차가 수정되었습니다.");
    }

    @PostMapping("/chapters/{id}/publish")
    @Operation(summary = "회차 발행", description = "회차를 발행합니다.")
    public ApiResponse<ChapterResponse> publish(
            @PathVariable Long id,
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        ChapterResponse response = chapterService.publish(id, userPrincipal.getId());
        return ApiResponse.success(response, "회차가 발행되었습니다.");
    }

    @PostMapping("/chapters/{id}/schedule")
    @Operation(summary = "회차 예약 발행", description = "회차 예약 발행 시간을 설정합니다.")
    public ApiResponse<ChapterResponse> schedule(
            @PathVariable Long id,
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @RequestParam LocalDateTime scheduledAt) {
        ChapterResponse response = chapterService.schedule(id, userPrincipal.getId(), scheduledAt);
        return ApiResponse.success(response, "예약 발행이 설정되었습니다.");
    }
}
