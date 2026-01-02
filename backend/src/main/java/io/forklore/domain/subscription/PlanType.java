package io.forklore.domain.subscription;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

/**
 * 구독 요금제 타입
 */
@Getter
@RequiredArgsConstructor
public enum PlanType {
    MONTHLY("월간", 30),
    YEARLY("연간", 365);

    private final String displayName;
    private final int durationDays;
}
