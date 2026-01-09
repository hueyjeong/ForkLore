package io.forklore.domain.chapter;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

/**
 * 회차 상태
 * - DRAFT: 초안
 * - SCHEDULED: 예약 발행
 * - PUBLISHED: 발행됨
 */
@Getter
@RequiredArgsConstructor
public enum ChapterStatus {
    DRAFT("초안"),
    SCHEDULED("예약"),
    PUBLISHED("발행됨");

    private final String displayName;
}
