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
import org.springframework.test.web.reactive.server.WebTestClient;

/**
 * 소설 E2E 테스트
 * - WebTestClient 사용 (수동 설정)
 * - 실제 서버 HTTP 요청/응답 검증
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("common")
@DisplayName("소설 E2E 테스트")
class NovelE2ETest {

    @LocalServerPort
    private int port;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    private WebTestClient webTestClient;

    @BeforeEach
    void setUp() {
        // WebTestClient를 수동으로 bindToServer() 방식으로 생성
        webTestClient = WebTestClient.bindToServer()
                .baseUrl("http://localhost:" + port)
                .build();
        userRepository.deleteAll();
    }

    @Nested
    @DisplayName("소설 목록 조회")
    class NovelList {

        @Test
        @DisplayName("인증 없이 소설 목록 조회 가능")
        void getNovelListWithoutAuth() {
            webTestClient.get().uri("/api/novels")
                    .exchange()
                    .expectStatus().isOk()
                    .expectBody()
                    .jsonPath("$.data").exists();
        }

        @Test
        @DisplayName("장르별 소설 필터링")
        void filterNovelsByGenre() {
            webTestClient.get().uri("/api/novels?genre=FANTASY")
                    .exchange()
                    .expectStatus().isOk();
        }
    }

    @Nested
    @DisplayName("소설 생성")
    class CreateNovel {

        @Test
        @DisplayName("인증 없이 소설 생성 시 401 응답")
        void createNovelWithoutAuth() {
            String novelJson = """
                    {
                        "title": "테스트 소설",
                        "description": "설명",
                        "genre": "FANTASY",
                        "ageRating": "ALL",
                        "allowBranching": true
                    }
                    """;

            webTestClient.post().uri("/api/novels")
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(novelJson)
                    .exchange()
                    .expectStatus().isUnauthorized();
        }

        @Test
        @DisplayName("인증된 작가가 소설 생성 성공")
        void createNovelWithAuth() {
            // given - 작가 생성 및 로그인
            User author = createAuthor();
            String token = getAuthToken(author);

            String novelJson = """
                    {
                        "title": "새로운 판타지 소설",
                        "description": "멋진 모험 이야기",
                        "genre": "FANTASY",
                        "ageRating": "ALL",
                        "allowBranching": true
                    }
                    """;

            // when & then
            webTestClient.post().uri("/api/novels")
                    .header("Authorization", "Bearer " + token)
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(novelJson)
                    .exchange()
                    .expectStatus().isCreated()
                    .expectBody()
                    .jsonPath("$.data.title").isEqualTo("새로운 판타지 소설")
                    .jsonPath("$.data.genre").isEqualTo("FANTASY");
        }
    }

    @Nested
    @DisplayName("소설 상세 조회")
    class NovelDetail {

        @Test
        @DisplayName("존재하지 않는 소설 조회 시 404 응답")
        void getNovelDetailNotFound() {
            webTestClient.get().uri("/api/novels/99999")
                    .exchange()
                    .expectStatus().isNotFound();
        }
    }

    private User createAuthor() {
        User author = User.builder()
                .email("author@example.com")
                .password(passwordEncoder.encode("password"))
                .nickname("작가")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        return userRepository.save(author);
    }

    private String getAuthToken(User user) {
        String loginJson = String.format("""
                {"email": "%s", "password": "password"}
                """, user.getEmail());

        String response = webTestClient.post().uri("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(loginJson)
                .exchange()
                .expectStatus().isOk()
                .expectBody(String.class)
                .returnResult()
                .getResponseBody();

        if (response == null)
            return "";
        int start = response.indexOf("accessToken\":\"") + 14;
        int end = response.indexOf("\"", start);
        return response.substring(start, end);
    }
}
