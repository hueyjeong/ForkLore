package io.forklore.dto.response;

import io.forklore.domain.subscription.PlanType;
import io.forklore.domain.subscription.Subscription;
import io.forklore.domain.subscription.SubscriptionStatus;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "구독 정보 응답")
public class SubscriptionResponse {

    @Schema(description = "구독 ID")
    private Long id;

    @Schema(description = "요금제 타입")
    private PlanType planType;

    @Schema(description = "시작일")
    private LocalDate startDate;

    @Schema(description = "종료일")
    private LocalDate endDate;

    @Schema(description = "상태")
    private SubscriptionStatus status;

    @Schema(description = "자동 갱신 여부")
    private boolean autoRenew;

    @Schema(description = "남은 일수")
    private long remainingDays;

    @Schema(description = "활성화 여부")
    private boolean active;

    public static SubscriptionResponse from(Subscription subscription) {
        return SubscriptionResponse.builder()
                .id(subscription.getId())
                .planType(subscription.getPlanType())
                .startDate(subscription.getStartDate())
                .endDate(subscription.getEndDate())
                .status(subscription.getStatus())
                .autoRenew(subscription.isAutoRenew())
                .remainingDays(subscription.getRemainingDays())
                .active(subscription.isActive())
                .build();
    }
}
