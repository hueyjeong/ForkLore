package io.forklore.dto.request;

import io.forklore.domain.subscription.PlanType;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotNull;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@Schema(description = "구독 생성 요청")
public class SubscriptionCreateRequest {

    @NotNull(message = "요금제 타입은 필수입니다")
    @Schema(description = "요금제 타입", example = "MONTHLY")
    private PlanType planType;

    @Schema(description = "자동 갱신 여부", example = "true")
    private boolean autoRenew = true;

    @Builder
    public SubscriptionCreateRequest(PlanType planType, boolean autoRenew) {
        this.planType = planType;
        this.autoRenew = autoRenew;
    }
}
