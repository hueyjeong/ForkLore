package io.forklore.domain.branch;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

/**
 * 정사 편입 상태
 * - NON_CANON: 비정사 (기본)
 * - CANDIDATE: 정사 편입 후보
 * - MERGED: 정사에 편입됨
 */
@Getter
@RequiredArgsConstructor
public enum CanonStatus {
    NON_CANON("비정사"),
    CANDIDATE("후보"),
    MERGED("편입됨");

    private final String displayName;
}
