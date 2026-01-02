package io.forklore.security.jwt;

import io.forklore.domain.user.UserRole;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;

import java.util.Collections;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

class JwtTokenProviderTest {

    private JwtTokenProvider jwtTokenProvider;
    private JwtProperties jwtProperties;
    private UserDetailsService userDetailsService;

    @BeforeEach
    void setUp() {
        jwtProperties = new JwtProperties();
        jwtProperties.setSecret("testSecrettestSecrettestSecrettestSecrettestSecret");
        jwtProperties.setAccessTokenExpiration(3600000L); // 1h
        jwtProperties.setRefreshTokenExpiration(604800000L); // 7d

        userDetailsService = mock(UserDetailsService.class);
        jwtTokenProvider = new JwtTokenProvider(jwtProperties, userDetailsService);
    }

    @Test
    @DisplayName("Access Token 생성 및 검증 성공")
    void createAndValidateAccessToken() {
        // given
        String email = "test@example.com";
        String role = UserRole.READER.getKey();
        
        UserDetails userDetails = mock(UserDetails.class);
        given(userDetailsService.loadUserByUsername(email)).willReturn(userDetails);
        given(userDetails.getAuthorities()).willReturn(Collections.emptyList());

        // when
        String token = jwtTokenProvider.createAccessToken(email, role);

        // then
        assertThat(token).isNotNull();
        assertThat(jwtTokenProvider.validateToken(token)).isTrue();
        assertThat(jwtTokenProvider.getAuthentication(token)).isNotNull();
        verify(userDetailsService).loadUserByUsername(email);
    }

    @Test
    @DisplayName("Refresh Token 생성 및 검증 성공")
    void createAndValidateRefreshToken() {
        // given
        String email = "test@example.com";

        // when
        String token = jwtTokenProvider.createRefreshToken(email);

        // then
        assertThat(token).isNotNull();
        assertThat(jwtTokenProvider.validateToken(token)).isTrue();
    }
    
    @Test
    @DisplayName("잘못된 서명 토큰 검증 실패")
    void invalidSignature() {
        // given
        JwtProperties otherProps = new JwtProperties();
        otherProps.setSecret("otherSecretKeyotherSecretKeyotherSecretKeyotherSecretKey");
        otherProps.setAccessTokenExpiration(1000L);
        // UserDetailsService는 검증 로직에 사용되지 않으므로 null 주입 가능
        JwtTokenProvider otherProvider = new JwtTokenProvider(otherProps, null);
        String token = otherProvider.createAccessToken("test@example.com", "ROLE_USER");
        
        // then
        assertThat(jwtTokenProvider.validateToken(token)).isFalse();
    }
}
