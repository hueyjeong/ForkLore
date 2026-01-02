package io.forklore.e2e;

import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.client.RestTestClient;

/**
 * E2E 테스트 (End-to-End Test)
 * - @SpringBootTest(webEnvironment = RANDOM_PORT)로 실제 서버 구동
 * - RestTestClient로 실제 HTTP 요청/응답 검증 (Spring Framework 7)
 * - 인증 흐름 전체 테스트
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("common")
@DisplayName("인증 E2E 테스트")
class AuthE2ETest {

    @LocalServerPort
    private int port;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    private RestTestClient restTestClient;

    @BeforeEach
    void setUp() {
        // bindToServer로 실제 HTTP 서버에 연결
        restTestClient = RestTestClient.bindToServer()
                .baseUrl("http://localhost:" + port + "/api")
                .build();
        userRepository.deleteAll();
    }

    @Nested
    @DisplayName("회원가입 → 로그인 플로우")
    class SignUpLoginFlow {

        @Test
        @DisplayName("회원가입 후 로그인 성공해야 함")
        void signUpThenLogin() {
            // given - 회원가입
            String signUpJson = """
                    {
                        "email": "e2e@example.com",
                        "password": "password123!",
                        "nickname": "e2e테스터"
                    }
                    """;

            restTestClient.post().uri("/auth/signup")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(signUpJson)
                    .exchange()
                    .expectStatus().isCreated();

            // when - 로그인
            String loginJson = """
                    {
                        "email": "e2e@example.com",
                        "password": "password123!"
                    }
                    """;

            // then
            restTestClient.post().uri("/auth/login")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(loginJson)
                    .exchange()
                    .expectStatus().isOk()
                    .expectBody()
                    .jsonPath("$.data.accessToken").isNotEmpty();
        }
    }

    @Nested
    @DisplayName("인증 실패 시나리오")
    class AuthFailureScenarios {

        @Test
        @DisplayName("잘못된 비밀번호로 로그인 실패해야 함")
        void loginWithWrongPassword() {
            // given - 사용자 생성
            User user = User.builder()
                    .email("wrong-pw@example.com")
                    .password(passwordEncoder.encode("correct-password"))
                    .nickname("테스터")
                    .role(UserRole.READER)
                    .authProvider(AuthProvider.LOCAL)
                    .build();
            userRepository.save(user);

            // when
            String loginJson = """
                    {
                        "email": "wrong-pw@example.com",
                        "password": "wrong-password"
                    }
                    """;

            // then
            restTestClient.post().uri("/auth/login")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(loginJson)
                    .exchange()
                    .expectStatus().isUnauthorized();
        }

        @Test
        @DisplayName("존재하지 않는 이메일로 로그인 실패해야 함")
        void loginWithNonExistentEmail() {
            // when
            String loginJson = """
                    {
                        "email": "nonexistent@example.com",
                        "password": "password"
                    }
                    """;

            // then
            restTestClient.post().uri("/auth/login")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(loginJson)
                    .exchange()
                    .expectStatus().isUnauthorized();
        }
    }

    @Nested
    @DisplayName("인증된 요청 테스트")
    class AuthenticatedRequests {

        @Test
        @DisplayName("토큰 없이 보호된 API 접근 시 401 응답")
        void accessProtectedApiWithoutToken() {
            restTestClient.get().uri("/users/me")
                    .exchange()
                    .expectStatus().isUnauthorized();
        }
    }
}
