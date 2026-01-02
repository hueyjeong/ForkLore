package io.forklore.domain.branch;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

/**
 * 연결 요청 상태
 * - PENDING: 대기 중
 * - APPROVED: 승인됨
 * - REJECTED: 거절됨
 */
@Getter
@RequiredArgsConstructor
public enum LinkRequestStatus {
    PENDING("대기중"),
    APPROVED("승인됨"),
    REJECTED("거절됨");

    private final String displayName;
}
