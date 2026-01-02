package io.forklore.security.oauth2;

import io.forklore.domain.refresh.RefreshToken;
import io.forklore.domain.user.User;
import io.forklore.repository.refresh.RefreshTokenRepository;
import io.forklore.security.UserPrincipal;
import io.forklore.security.jwt.JwtProperties;
import io.forklore.security.jwt.JwtTokenProvider;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.security.core.Authentication;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class OAuth2SuccessHandlerTest {

    @InjectMocks
    private OAuth2SuccessHandler oAuth2SuccessHandler;

    @Mock
    private JwtTokenProvider jwtTokenProvider;

    @Mock
    private RefreshTokenRepository refreshTokenRepository;

    @Mock
    private JwtProperties jwtProperties;
    
    @Mock
    private Authentication authentication;

    @Test
    @DisplayName("로그인 성공 시 토큰 발급 및 리다이렉트")
    void onAuthenticationSuccess_shouldRedirectWithTokens() throws Exception {
        // given
        MockHttpServletRequest request = new MockHttpServletRequest();
        MockHttpServletResponse response = new MockHttpServletResponse();
        
        User user = User.builder()
                .email("test@mail.com")
                .nickname("Tester")
                .role(io.forklore.domain.user.UserRole.READER)
                .build();
        UserPrincipal principal = mock(UserPrincipal.class);
        given(principal.getUser()).willReturn(user);
        given(authentication.getPrincipal()).willReturn(principal);
        
        given(jwtTokenProvider.createAccessToken(any(), any())).willReturn("access-token");
        given(jwtTokenProvider.createRefreshToken(any())).willReturn("refresh-token");
        given(jwtProperties.getRefreshTokenExpiration()).willReturn(3600000L);

        // when
        oAuth2SuccessHandler.onAuthenticationSuccess(request, response, authentication);

        // then
        String redirectUrl = response.getRedirectedUrl();
        assertThat(redirectUrl).contains("/oauth2/redirect");
        assertThat(redirectUrl).contains("accessToken=access-token");
        assertThat(redirectUrl).contains("refreshToken=refresh-token");
        
        verify(refreshTokenRepository).save(any(RefreshToken.class));
    }
}
