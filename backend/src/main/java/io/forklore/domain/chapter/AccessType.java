package io.forklore.domain.chapter;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

/**
 * 회차 접근 타입
 * - FREE: 무료
 * - SUBSCRIPTION: 구독 필요
 */
@Getter
@RequiredArgsConstructor
public enum AccessType {
    FREE("무료"),
    SUBSCRIPTION("구독");

    private final String displayName;
}
