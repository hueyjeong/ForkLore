package io.forklore.global.error;

/**
 * 엔티티를 찾을 수 없을 때 발생하는 예외
 */
public class EntityNotFoundException extends BusinessException {
    public EntityNotFoundException(String message) {
        super(message, CommonErrorCode.ENTITY_NOT_FOUND);
    }

    public EntityNotFoundException() {
        super(CommonErrorCode.ENTITY_NOT_FOUND);
    }
}
