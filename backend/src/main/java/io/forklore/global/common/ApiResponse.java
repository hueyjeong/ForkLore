package io.forklore.global.common;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 전역 공통 응답 포맷
 */
@Getter
@NoArgsConstructor(access = AccessLevel.PRIVATE)
@Schema(description = "공통 API 응답")
public class ApiResponse<T> {

    @Schema(description = "성공 여부", example = "true")
    private boolean success;

    @Schema(description = "응답 데이터")
    private T data;

    @Schema(description = "응답 메시지", example = "요청이 성공적으로 처리되었습니다.")
    private String message;

    @Schema(description = "서버 응답 시간")
    private LocalDateTime serverTime;

    private ApiResponse(boolean success, T data, String message) {
        this.success = success;
        this.data = data;
        this.message = message;
        this.serverTime = LocalDateTime.now();
    }

    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(true, data, "요청이 성공적으로 처리되었습니다.");
    }

    public static <T> ApiResponse<T> success(T data, String message) {
        return new ApiResponse<>(true, data, message);
    }

    public static ApiResponse<Void> success() {
        return new ApiResponse<>(true, null, "요청이 성공적으로 처리되었습니다.");
    }
}
