package io.forklore.controller;

import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.NovelStatus;
import io.forklore.dto.request.NovelCreateRequest;
import io.forklore.dto.request.NovelUpdateRequest;
import io.forklore.dto.response.NovelResponse;
import io.forklore.dto.response.NovelSummaryResponse;
import io.forklore.global.common.ApiResponse;
import io.forklore.security.UserPrincipal;
import io.forklore.service.novel.NovelService;
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
@RequestMapping("/novels")
@RequiredArgsConstructor
@Tag(name = "Novel", description = "소설 관리 API")
public class NovelController {

    private final NovelService novelService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "소설 생성", description = "새로운 소설을 생성합니다.")
    public ApiResponse<NovelResponse> create(
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @Valid @RequestBody NovelCreateRequest request) {
        NovelResponse response = novelService.create(userPrincipal.getId(), request);
        return ApiResponse.success(response, "소설이 생성되었습니다.");
    }

    @GetMapping
    @Operation(summary = "소설 목록 조회", description = "소설 목록을 조회합니다. 장르, 상태로 필터링 가능합니다.")
    public ApiResponse<Page<NovelSummaryResponse>> getList(
            @RequestParam(required = false) Genre genre,
            @RequestParam(required = false) NovelStatus status,
            @PageableDefault(size = 20) Pageable pageable) {
        Page<NovelSummaryResponse> response = novelService.getList(genre, status, pageable);
        return ApiResponse.success(response);
    }

    @GetMapping("/{id}")
    @Operation(summary = "소설 상세 조회", description = "소설 상세 정보를 조회합니다.")
    public ApiResponse<NovelResponse> getDetail(@PathVariable Long id) {
        NovelResponse response = novelService.getDetail(id);
        return ApiResponse.success(response);
    }

    @PatchMapping("/{id}")
    @Operation(summary = "소설 수정", description = "소설 정보를 수정합니다. 작가 본인만 가능합니다.")
    public ApiResponse<NovelResponse> update(
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @PathVariable Long id,
            @Valid @RequestBody NovelUpdateRequest request) {
        NovelResponse response = novelService.update(userPrincipal.getId(), id, request);
        return ApiResponse.success(response, "소설이 수정되었습니다.");
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "소설 삭제", description = "소설을 삭제합니다. 작가 본인만 가능합니다.")
    public ApiResponse<Void> delete(
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @PathVariable Long id) {
        novelService.delete(userPrincipal.getId(), id);
        return ApiResponse.success();
    }
}
