package io.forklore.domain.branch;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

/**
 * 브랜치 타입
 * - MAIN: 원작 정사
 * - SIDE_STORY: 외전
 * - FAN_FIC: 팬픽
 * - IF_STORY: IF 스토리
 */
@Getter
@RequiredArgsConstructor
public enum BranchType {
    MAIN("메인", "원작 정사"),
    SIDE_STORY("외전", "공식 외전"),
    FAN_FIC("팬픽", "팬 창작물"),
    IF_STORY("IF", "IF 스토리");

    private final String displayName;
    private final String description;
}
