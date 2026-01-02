package io.forklore.security.jwt;

import io.forklore.domain.user.UserRole;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class JwtTokenProviderTest {

    private JwtTokenProvider jwtTokenProvider;
    private JwtProperties jwtProperties;

    @BeforeEach
    void setUp() {
        jwtProperties = new JwtProperties();
        jwtProperties.setSecret("testSecrettestSecrettestSecrettestSecrettestSecret");
        jwtProperties.setAccessTokenExpiration(3600000L); // 1h
        jwtProperties.setRefreshTokenExpiration(604800000L); // 7d

        jwtTokenProvider = new JwtTokenProvider(jwtProperties);
    }

    @Test
    @DisplayName("Access Token 생성 및 검증 성공")
    void createAndValidateAccessToken() {
        // given
        String email = "test@example.com";
        String role = UserRole.READER.getKey();

        // when
        String token = jwtTokenProvider.createAccessToken(email, role);

        // then
        assertThat(token).isNotNull();
        assertThat(jwtTokenProvider.validateToken(token)).isTrue();
        assertThat(jwtTokenProvider.getAuthentication(token).getName()).isEqualTo(email);
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
        JwtTokenProvider otherProvider = new JwtTokenProvider(otherProps);
        String token = otherProvider.createAccessToken("test@example.com", "ROLE_USER");
        
        // then
        assertThat(jwtTokenProvider.validateToken(token)).isFalse();
    }
}
