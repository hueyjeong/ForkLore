package io.forklore.global.common;

import java.time.LocalDateTime;

/**
 * 소프트 삭제(Soft Delete) 기능을 지원하는 엔티티를 위한 인터페이스
 */
public interface SoftDeletable {
    LocalDateTime getDeletedAt();
    void setDeletedAt(LocalDateTime deletedAt);
    
    default boolean isDeleted() {
        return getDeletedAt() != null;
    }
}
