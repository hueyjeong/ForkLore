package io.forklore.global.error;

/**
 * 권한이 없을 때 발생하는 예외
 */
public class UnauthorizedException extends BusinessException {
    public UnauthorizedException(String message) {
        super(message, CommonErrorCode.ACCESS_DENIED);
    }

    public UnauthorizedException() {
        super(CommonErrorCode.ACCESS_DENIED);
    }
}
