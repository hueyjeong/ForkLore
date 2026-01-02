package io.forklore.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class TokenRefreshRequest {

    @NotBlank
    private String refreshToken;

    @Builder
    public TokenRefreshRequest(String refreshToken) {
        this.refreshToken = refreshToken;
    }
}
