package io.forklore.dto.request;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Size;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@Schema(description = "브랜치 연결 요청")
public class LinkRequestCreateRequest {

    @Size(max = 1000, message = "요청 메시지는 1000자 이하여야 합니다")
    @Schema(description = "요청 메시지")
    private String requestMessage;

    @Builder
    public LinkRequestCreateRequest(String requestMessage) {
        this.requestMessage = requestMessage;
    }
}
