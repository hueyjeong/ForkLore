package io.forklore.controller;

import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.novel.NovelRepository;
import io.forklore.domain.novel.NovelStatus;
import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.dto.request.NovelCreateRequest;
import io.forklore.dto.request.NovelUpdateRequest;
import io.forklore.dto.response.NovelResponse;

import io.forklore.global.common.ApiResponse;
import io.forklore.repository.UserRepository;
import io.forklore.security.jwt.JwtTokenProvider;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.core.ParameterizedTypeReference;

import org.springframework.http.*;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.test.context.ActiveProfiles;

import org.springframework.web.client.RestTemplate;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("common")
class NovelControllerTest {

        @LocalServerPort
        private int port;

        private RestTemplate restTemplate;

        @Autowired
        private JwtTokenProvider jwtTokenProvider;

        @Autowired
        private UserRepository userRepository;

        @Autowired
        private NovelRepository novelRepository;

        private String baseUrl;
        private User author;
        private String accessToken;

        @BeforeEach
        void setUp() {
                restTemplate = new RestTemplate();
                restTemplate.setRequestFactory(new JdkClientHttpRequestFactory());
                baseUrl = "http://localhost:" + port + "/api/novels";

                // 테스트 사용자 생성 (트랜잭션 외부에서 직접 저장)
                author = userRepository.findByEmail("novel-test-author@example.com")
                                .orElseGet(() -> {
                                        User newAuthor = User.builder()
                                                        .email("novel-test-author@example.com")
                                                        .password("password")
                                                        .nickname("소설테스트작가")
                                                        .role(UserRole.AUTHOR)
                                                        .authProvider(AuthProvider.LOCAL)
                                                        .build();
                                        return userRepository.save(newAuthor);
                                });

                // JWT 토큰 생성
                accessToken = jwtTokenProvider.createAccessToken(author.getEmail(), author.getRole().getKey());
        }

        @Test
        @DisplayName("POST /novels - 소설 생성")
        void create() {
                // given
                NovelCreateRequest request = NovelCreateRequest.builder()
                                .title("테스트 소설 - " + System.currentTimeMillis())
                                .description("테스트 설명")
                                .genre(Genre.FANTASY)
                                .ageRating(AgeRating.ALL)
                                .allowBranching(true)
                                .build();

                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);
                headers.setBearerAuth(accessToken);

                HttpEntity<NovelCreateRequest> entity = new HttpEntity<>(request, headers);

                // when
                ResponseEntity<ApiResponse<NovelResponse>> response = restTemplate.exchange(
                                baseUrl,
                                HttpMethod.POST,
                                entity,
                                new ParameterizedTypeReference<>() {
                                });

                // then
                assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
                assertThat(response.getBody()).isNotNull();
                assertThat(response.getBody().isSuccess()).isTrue();
                assertThat(response.getBody().getData().getTitle()).startsWith("테스트 소설 -");
        }

        @Test
        @DisplayName("GET /novels - 소설 목록 조회")
        void getList() {
                // given - 테스트 데이터 생성
                createTestNovel("목록테스트소설-" + System.currentTimeMillis());

                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);

                HttpEntity<Void> entity = new HttpEntity<>(headers);

                // when
                ResponseEntity<String> response = restTemplate.exchange(
                                baseUrl + "?page=0&size=10",
                                HttpMethod.GET,
                                entity,
                                String.class);

                // then
                assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
                assertThat(response.getBody()).isNotNull();
                assertThat(response.getBody()).contains("success");
        }

        @Test
        @DisplayName("GET /novels/{id} - 소설 상세 조회")
        void getDetail() {
                // given
                Novel novel = createTestNovel("상세조회테스트-" + System.currentTimeMillis());

                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);

                HttpEntity<Void> entity = new HttpEntity<>(headers);

                // when
                ResponseEntity<ApiResponse<NovelResponse>> response = restTemplate.exchange(
                                baseUrl + "/" + novel.getId(),
                                HttpMethod.GET,
                                entity,
                                new ParameterizedTypeReference<>() {
                                });

                // then
                assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
                assertThat(response.getBody()).isNotNull();
                assertThat(response.getBody().isSuccess()).isTrue();
                assertThat(response.getBody().getData().getId()).isEqualTo(novel.getId());
        }

        @Test
        @DisplayName("PATCH /novels/{id} - 소설 수정")
        void update() {
                // given
                Novel novel = createTestNovel("수정전제목-" + System.currentTimeMillis());

                NovelUpdateRequest request = NovelUpdateRequest.builder()
                                .title("수정후제목")
                                .status(NovelStatus.COMPLETED)
                                .build();

                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);
                headers.setBearerAuth(accessToken);

                HttpEntity<NovelUpdateRequest> entity = new HttpEntity<>(request, headers);

                // when
                ResponseEntity<ApiResponse<NovelResponse>> response = restTemplate.exchange(
                                baseUrl + "/" + novel.getId(),
                                HttpMethod.PATCH,
                                entity,
                                new ParameterizedTypeReference<>() {
                                });

                // then
                assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
                assertThat(response.getBody()).isNotNull();
                assertThat(response.getBody().isSuccess()).isTrue();
                assertThat(response.getBody().getData().getTitle()).isEqualTo("수정후제목");
                assertThat(response.getBody().getData().getStatus()).isEqualTo(NovelStatus.COMPLETED);
        }

        @Test
        @DisplayName("DELETE /novels/{id} - 소설 삭제")
        void delete() {
                // given
                Novel novel = createTestNovel("삭제테스트-" + System.currentTimeMillis());
                Long novelId = novel.getId();

                HttpHeaders headers = new HttpHeaders();
                headers.setBearerAuth(accessToken);

                HttpEntity<Void> entity = new HttpEntity<>(headers);

                // when
                ResponseEntity<ApiResponse<Void>> response = restTemplate.exchange(
                                baseUrl + "/" + novelId,
                                HttpMethod.DELETE,
                                entity,
                                new ParameterizedTypeReference<>() {
                                });

                // then
                assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
                assertThat(response.getBody()).isNotNull();
                assertThat(response.getBody().isSuccess()).isTrue();

                // 소프트 삭제 확인
                assertThat(novelRepository.findById(novelId)).isEmpty();
        }

        private Novel createTestNovel(String title) {
                Novel novel = Novel.builder()
                                .author(author)
                                .title(title)
                                .genre(Genre.FANTASY)
                                .ageRating(AgeRating.ALL)
                                .allowBranching(true)
                                .build();
                return novelRepository.save(novel);
        }
}
