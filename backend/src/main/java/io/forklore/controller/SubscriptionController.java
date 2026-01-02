package io.forklore.controller;

import io.forklore.domain.subscription.PlanType;
import io.forklore.dto.request.SubscriptionCreateRequest;
import io.forklore.dto.response.PurchaseResponse;
import io.forklore.dto.response.SubscriptionResponse;
import io.forklore.global.common.ApiResponse;
import io.forklore.security.UserPrincipal;
import io.forklore.service.access.AccessService;
import io.forklore.service.purchase.PurchaseService;
import io.forklore.service.subscription.SubscriptionService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@Tag(name = "Subscription & Purchase", description = "구독 및 구매 관리 API")
public class SubscriptionController {

    private final SubscriptionService subscriptionService;
    private final PurchaseService purchaseService;
    private final AccessService accessService;

    // ==================== 구독 API ====================

    @GetMapping("/users/me/subscription")
    @Operation(summary = "내 구독 상태 조회", description = "현재 로그인한 사용자의 구독 상태를 조회합니다.")
    public ApiResponse<SubscriptionResponse> getMySubscription(
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        return subscriptionService.getStatus(userPrincipal.getId())
                .map(ApiResponse::success)
                .orElseGet(() -> ApiResponse.success(null, "활성 구독이 없습니다."));
    }

    @GetMapping("/users/me/subscription/history")
    @Operation(summary = "구독 내역 조회", description = "구독 내역을 조회합니다.")
    public ApiResponse<List<SubscriptionResponse>> getSubscriptionHistory(
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        List<SubscriptionResponse> history = subscriptionService.getHistory(userPrincipal.getId());
        return ApiResponse.success(history);
    }

    @PostMapping("/subscriptions")
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "구독 가입", description = "새로운 구독을 생성합니다.")
    public ApiResponse<SubscriptionResponse> subscribe(
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @Valid @RequestBody SubscriptionCreateRequest request) {
        SubscriptionResponse response = subscriptionService.subscribe(
                userPrincipal.getId(),
                request.getPlanType(),
                request.isAutoRenew());
        return ApiResponse.success(response, "구독이 시작되었습니다.");
    }

    @DeleteMapping("/subscriptions/current")
    @Operation(summary = "구독 취소", description = "현재 구독을 취소합니다. 만료일까지는 이용 가능합니다.")
    public ApiResponse<SubscriptionResponse> cancelSubscription(
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        SubscriptionResponse response = subscriptionService.cancel(userPrincipal.getId());
        return ApiResponse.success(response, "구독이 취소되었습니다. 만료일까지는 이용 가능합니다.");
    }

    @PatchMapping("/subscriptions/current/plan")
    @Operation(summary = "요금제 변경", description = "현재 구독의 요금제를 변경합니다.")
    public ApiResponse<SubscriptionResponse> changePlan(
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @RequestParam PlanType planType) {
        SubscriptionResponse response = subscriptionService.changePlan(userPrincipal.getId(), planType);
        return ApiResponse.success(response, "요금제가 변경되었습니다.");
    }

    // ==================== 구매 API ====================

    @GetMapping("/users/me/purchases")
    @Operation(summary = "구매 내역 조회", description = "내 구매 내역을 조회합니다.")
    public ApiResponse<List<PurchaseResponse>> getMyPurchases(
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        List<PurchaseResponse> purchases = purchaseService.getPurchaseList(userPrincipal.getId());
        return ApiResponse.success(purchases);
    }

    @PostMapping("/chapters/{chapterId}/purchase")
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "회차 구매", description = "개별 회차를 구매합니다.")
    public ApiResponse<PurchaseResponse> purchaseChapter(
            @PathVariable Long chapterId,
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        PurchaseResponse response = purchaseService.purchase(userPrincipal.getId(), chapterId);
        return ApiResponse.success(response, "회차를 구매했습니다.");
    }

    // ==================== 접근 권한 확인 API ====================

    @GetMapping("/chapters/{chapterId}/access")
    @Operation(summary = "회차 접근 권한 확인", description = "해당 회차에 대한 접근 권한을 확인합니다.")
    public ApiResponse<AccessService.AccessResult> checkAccess(
            @PathVariable Long chapterId,
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        Long userId = userPrincipal != null ? userPrincipal.getId() : null;
        AccessService.AccessResult result = accessService.checkAccess(userId, chapterId);
        return ApiResponse.success(result);
    }
}
