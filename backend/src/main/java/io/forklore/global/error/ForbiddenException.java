package io.forklore.global.error;

/**
 * 접근 권한 부족 예외 (403 Forbidden)
 */
public class ForbiddenException extends BusinessException {

    public ForbiddenException() {
        super("이 콘텐츠에 대한 접근 권한이 없습니다.", CommonErrorCode.ACCESS_DENIED);
    }

    public ForbiddenException(String message) {
        super(message, CommonErrorCode.ACCESS_DENIED);
    }
}
