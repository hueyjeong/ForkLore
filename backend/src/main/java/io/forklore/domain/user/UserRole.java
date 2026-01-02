package io.forklore.domain.user;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public enum UserRole {
    READER("ROLE_READER", "일반 독자"),
    AUTHOR("ROLE_AUTHOR", "작가"),
    ADMIN("ROLE_ADMIN", "관리자");

    private final String key;
    private final String title;
}
