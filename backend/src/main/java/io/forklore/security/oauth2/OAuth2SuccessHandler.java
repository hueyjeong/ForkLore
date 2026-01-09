package io.forklore.security.oauth2;

import io.forklore.domain.refresh.RefreshToken;
import io.forklore.domain.user.User;
import io.forklore.repository.refresh.RefreshTokenRepository;
import io.forklore.security.UserPrincipal;
import io.forklore.security.jwt.JwtProperties;
import io.forklore.security.jwt.JwtTokenProvider;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;
import org.springframework.web.util.UriComponentsBuilder;

import java.io.IOException;
import java.time.Instant;

@Slf4j
@Component
@RequiredArgsConstructor
public class OAuth2SuccessHandler extends SimpleUrlAuthenticationSuccessHandler {

    private final JwtTokenProvider jwtTokenProvider;
    private final RefreshTokenRepository refreshTokenRepository;
    private final JwtProperties jwtProperties;

    // 프론트엔드 리다이렉트 URI (임시 하드코딩, 환경변수화 권장)
    private static final String REDIRECT_URI = "http://localhost:3000/oauth2/redirect";

    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response,
            Authentication authentication) throws IOException, ServletException {
        UserPrincipal principal = (UserPrincipal) authentication.getPrincipal();
        User user = principal.getUser();

        String accessToken = jwtTokenProvider.createAccessToken(user.getEmail(), user.getRoleKey());
        String refreshToken = jwtTokenProvider.createRefreshToken(user.getEmail());

        saveRefreshToken(user, refreshToken);

        String targetUrl = UriComponentsBuilder.fromUriString(REDIRECT_URI)
                .queryParam("accessToken", accessToken)
                .queryParam("refreshToken", refreshToken)
                .build().toUriString();

        getRedirectStrategy().sendRedirect(request, response, targetUrl);
    }

    private void saveRefreshToken(User user, String token) {
        refreshTokenRepository.deleteByUser(user);
        refreshTokenRepository.save(RefreshToken.builder()
                .user(user)
                .token(token)
                .expiryDate(Instant.now().plusMillis(jwtProperties.getRefreshTokenExpiration()))
                .build());
    }
}
