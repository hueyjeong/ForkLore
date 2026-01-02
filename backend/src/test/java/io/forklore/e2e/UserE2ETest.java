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
 * 사용자 E2E 테스트
 * - 사용자 프로필 조회/수정
 * - 비밀번호 변경
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("common")
@DisplayName("사용자 E2E 테스트")
class UserE2ETest {

    @LocalServerPort
    private int port;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    private RestTestClient restTestClient;

    @BeforeEach
    void setUp() {
        restTestClient = RestTestClient.bindToServer()
                .baseUrl("http://localhost:" + port + "/api")
                .build();
        userRepository.deleteAll();
    }

    @Nested
    @DisplayName("프로필 조회")
    class GetProfile {

        @Test
        @DisplayName("인증 없이 프로필 조회 시 401 응답")
        void getProfileWithoutAuth() {
            restTestClient.get().uri("/users/me")
                    .exchange()
                    .expectStatus().isUnauthorized();
        }

        @Test
        @DisplayName("인증된 사용자 프로필 조회 성공")
        void getProfileWithAuth() {
            // given
            User user = createUserAndLogin();
            String token = getAuthToken(user);

            // when & then
            restTestClient.get().uri("/users/me")
                    .header("Authorization", "Bearer " + token)
                    .exchange()
                    .expectStatus().isOk()
                    .expectBody()
                    .jsonPath("$.data.email").isEqualTo(user.getEmail())
                    .jsonPath("$.data.nickname").isEqualTo(user.getNickname());
        }
    }

    @Nested
    @DisplayName("프로필 수정")
    class UpdateProfile {

        @Test
        @DisplayName("닉네임 변경 성공")
        void updateNickname() {
            // given
            User user = createUserAndLogin();
            String token = getAuthToken(user);

            String updateJson = """
                    {"nickname": "새로운닉네임"}
                    """;

            // when & then
            restTestClient.patch().uri("/users/me")
                    .header("Authorization", "Bearer " + token)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(updateJson)
                    .exchange()
                    .expectStatus().isOk()
                    .expectBody()
                    .jsonPath("$.data.nickname").isEqualTo("새로운닉네임");
        }
    }

    @Nested
    @DisplayName("비밀번호 변경")
    class ChangePassword {

        @Test
        @DisplayName("현재 비밀번호가 틀리면 실패")
        void changePasswordWithWrongCurrentPassword() {
            // given
            User user = createUserAndLogin();
            String token = getAuthToken(user);

            String changePasswordJson = """
                    {
                        "currentPassword": "wrong-password",
                        "newPassword": "new-password123!"
                    }
                    """;

            // when & then
            restTestClient.post().uri("/users/me/password")
                    .header("Authorization", "Bearer " + token)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(changePasswordJson)
                    .exchange()
                    .expectStatus().isBadRequest();
        }

        @Test
        @DisplayName("비밀번호 변경 성공 후 새 비밀번호로 로그인")
        void changePasswordSuccess() {
            // given
            User user = createUserAndLogin();
            String token = getAuthToken(user);

            String changePasswordJson = """
                    {
                        "currentPassword": "password",
                        "newPassword": "new-password123!"
                    }
                    """;

            // when - 비밀번호 변경
            restTestClient.post().uri("/users/me/password")
                    .header("Authorization", "Bearer " + token)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(changePasswordJson)
                    .exchange()
                    .expectStatus().isOk();

            // then - 새 비밀번호로 로그인
            String loginJson = String.format("""
                    {"email": "%s", "password": "new-password123!"}
                    """, user.getEmail());

            restTestClient.post().uri("/auth/login")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(loginJson)
                    .exchange()
                    .expectStatus().isOk()
                    .expectBody()
                    .jsonPath("$.data.accessToken").isNotEmpty();
        }
    }

    private User createUserAndLogin() {
        User user = User.builder()
                .email("user@example.com")
                .password(passwordEncoder.encode("password"))
                .nickname("테스터")
                .role(UserRole.READER)
                .authProvider(AuthProvider.LOCAL)
                .build();
        return userRepository.save(user);
    }

    private String getAuthToken(User user) {
        String loginJson = String.format("""
                {"email": "%s", "password": "password"}
                """, user.getEmail());

        byte[] responseBody = restTestClient.post().uri("/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .body(loginJson)
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .returnResult()
                .getResponseBody();

        if (responseBody == null)
            return "";
        String response = new String(responseBody);
        int start = response.indexOf("accessToken\":\"") + 14;
        int end = response.indexOf("\"", start);
        return response.substring(start, end);
    }
}
