package io.forklore.controller;

import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.dto.request.UpdatePasswordRequest;
import io.forklore.dto.request.UpdateProfileRequest;
import io.forklore.dto.response.UserResponse;
import io.forklore.global.common.ApiResponse;
import io.forklore.repository.UserRepository;
import io.forklore.security.jwt.JwtTokenProvider;
import io.forklore.service.user.UserService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.web.client.RestTemplate;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class UserControllerTest {

    @LocalServerPort
    private int port;

    private RestTemplate restTemplate = new RestTemplate();

    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    @Autowired
    private UserRepository userRepository;

    @MockitoBean
    private UserService userService;

    private String accessToken;
    private User user;

    @BeforeEach
    void setUp() {
        // PATCH 메서드 지원을 위해 JDK Client 사용 (Java 11+)
        restTemplate.setRequestFactory(new JdkClientHttpRequestFactory());

        userRepository.deleteAll();
        
        user = User.builder()
                .email("test@email.com")
                .password("password")
                .nickname("Tester")
                .role(UserRole.READER)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(user);

        accessToken = jwtTokenProvider.createAccessToken(user.getEmail(), user.getRoleKey());
    }

    private String getBaseUrl(String path) {
        return "http://localhost:" + port + path;
    }

    private HttpHeaders getHeaders() {
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(accessToken);
        headers.setContentType(MediaType.APPLICATION_JSON);
        return headers;
    }

    @Test
    @DisplayName("내 프로필 조회")
    void getMyProfile_success() {
        // given
        UserResponse response = UserResponse.builder()
                .id(user.getId())
                .email(user.getEmail())
                .nickname(user.getNickname())
                .build();

        given(userService.getProfile(any())).willReturn(response);

        // when
        ResponseEntity<ApiResponse<UserResponse>> result = restTemplate.exchange(
                getBaseUrl("/users/me"),
                HttpMethod.GET,
                new HttpEntity<>(getHeaders()),
                new ParameterizedTypeReference<ApiResponse<UserResponse>>() {}
        );

        // then
        assertThat(result.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(result.getBody()).isNotNull();
        assertThat(result.getBody().getData().getEmail()).isEqualTo("test@email.com");
    }

    @Test
    @DisplayName("내 프로필 수정")
    void updateProfile_success() {
        // given
        UpdateProfileRequest request = new UpdateProfileRequest("NewNick", "img");
        UserResponse response = UserResponse.builder()
                .nickname("NewNick")
                .build();

        given(userService.updateProfile(any(), any(UpdateProfileRequest.class))).willReturn(response);

        // when
        ResponseEntity<ApiResponse<UserResponse>> result = restTemplate.exchange(
                getBaseUrl("/users/me"),
                HttpMethod.PATCH,
                new HttpEntity<>(request, getHeaders()),
                new ParameterizedTypeReference<ApiResponse<UserResponse>>() {}
        );

        // then
        assertThat(result.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(result.getBody()).isNotNull();
        assertThat(result.getBody().getData().getNickname()).isEqualTo("NewNick");
    }

    @Test
    @DisplayName("비밀번호 변경")
    void updatePassword_success() {
        // given
        UpdatePasswordRequest request = new UpdatePasswordRequest("old", "new");

        // when
        ResponseEntity<ApiResponse<Void>> result = restTemplate.exchange(
                getBaseUrl("/users/me/password"),
                HttpMethod.POST,
                new HttpEntity<>(request, getHeaders()),
                new ParameterizedTypeReference<ApiResponse<Void>>() {}
        );

        // then
        assertThat(result.getStatusCode()).isEqualTo(HttpStatus.OK);
    }
}
