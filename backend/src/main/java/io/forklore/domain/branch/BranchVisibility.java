package io.forklore.domain.branch;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

/**
 * 브랜치 공개 상태
 * - PRIVATE: 비공개 (작성자만 접근)
 * - PUBLIC: 공개 (검색/URL로 접근)
 * - LINKED: 연결됨 (작품 페이지에 노출)
 */
@Getter
@RequiredArgsConstructor
public enum BranchVisibility {
    PRIVATE("비공개"),
    PUBLIC("공개"),
    LINKED("연결됨");

    private final String displayName;
}
