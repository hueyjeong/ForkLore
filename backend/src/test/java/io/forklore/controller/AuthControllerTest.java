package io.forklore.controller;

import io.forklore.dto.request.LoginRequest;
import io.forklore.dto.request.SignUpRequest;
import io.forklore.dto.response.TokenResponse;
import io.forklore.service.user.AuthService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class AuthControllerTest {

    @LocalServerPort
    private int port;

    private RestTemplate restTemplate = new RestTemplate();

    @MockitoBean
    private AuthService authService;

    private String getBaseUrl(String path) {
        return "http://localhost:" + port + path;
    }

    @Test
    @DisplayName("회원가입 API 성공")
    void signup_api_success() {
        // given
        SignUpRequest request = SignUpRequest.builder()
                .email("test@example.com")
                .password("password")
                .nickname("tester")
                .build();

        given(authService.signup(any(SignUpRequest.class))).willReturn(1L);

        // when
        ResponseEntity<String> response = restTemplate.postForEntity(getBaseUrl("/auth/signup"), request, String.class);

        // then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).contains("\"success\":true");
    }

    @Test
    @DisplayName("로그인 API 성공")
    void login_api_success() {
        // given
        LoginRequest request = LoginRequest.builder()
                .email("test@example.com")
                .password("password")
                .build();

        TokenResponse tokenResponse = TokenResponse.builder()
                .accessToken("access")
                .refreshToken("refresh")
                .expiresIn(3600L)
                .build();

        given(authService.login(any(LoginRequest.class))).willReturn(tokenResponse);

        // when
        ResponseEntity<String> response = restTemplate.postForEntity(getBaseUrl("/auth/login"), request, String.class);

        // then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).contains("\"accessToken\":\"access\"");
    }
}
