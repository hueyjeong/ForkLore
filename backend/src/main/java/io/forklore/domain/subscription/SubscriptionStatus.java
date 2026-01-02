package io.forklore.domain.subscription;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

/**
 * 구독 상태
 */
@Getter
@RequiredArgsConstructor
public enum SubscriptionStatus {
    ACTIVE("활성"),
    CANCELLED("취소예정"),
    EXPIRED("만료");

    private final String displayName;
}
