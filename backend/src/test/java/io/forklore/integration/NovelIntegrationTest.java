package io.forklore.integration;

import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.NovelStatus;
import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.dto.request.NovelCreateRequest;
import io.forklore.dto.response.NovelResponse;
import io.forklore.dto.response.NovelSummaryResponse;
import io.forklore.repository.UserRepository;
import io.forklore.service.novel.NovelService;
import jakarta.persistence.EntityManager;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * 통합 테스트 (Integration Test)
 * - @SpringBootTest로 전체 애플리케이션 컨텍스트 로드
 * - 실제 DB와 연동하여 여러 계층 간 상호작용 검증
 * - @Transactional로 테스트 후 롤백
 */
@SpringBootTest
@Transactional
@ActiveProfiles("test")
@DisplayName("소설 서비스 통합 테스트")
class NovelIntegrationTest {

    @Autowired
    private NovelService novelService;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private EntityManager em;

    private User author;

    @BeforeEach
    void setUp() {
        // 통합 테스트에서는 deleteAll 사용
        userRepository.deleteAll();

        author = User.builder()
                .email("integration-author@example.com")
                .password("password")
                .nickname("통합테스트작가")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(author);
    }

    @Nested
    @DisplayName("소설 생성 → 조회 플로우")
    class CreateAndRetrieveFlow {

        @Test
        @DisplayName("소설 생성 후 목록에서 조회 가능해야 함")
        void createNovelThenAppearInList() {
            // given
            NovelCreateRequest request = NovelCreateRequest.builder()
                    .title("통합테스트 소설")
                    .description("통합테스트 설명")
                    .genre(Genre.FANTASY)
                    .ageRating(AgeRating.ALL)
                    .allowBranching(true)
                    .build();

            // when
            novelService.create(author.getId(), request);
            em.flush();
            em.clear();

            Page<NovelSummaryResponse> list = novelService.getList(null, null, PageRequest.of(0, 10));

            // then
            assertThat(list.getTotalElements()).isGreaterThanOrEqualTo(1);
            assertThat(list.getContent())
                    .extracting(NovelSummaryResponse::getTitle)
                    .contains("통합테스트 소설");
        }

        @Test
        @DisplayName("소설 생성 후 상세 조회 가능해야 함")
        void createNovelThenGetDetail() {
            // given
            NovelCreateRequest request = NovelCreateRequest.builder()
                    .title("상세조회 테스트")
                    .description("설명")
                    .genre(Genre.ROMANCE)
                    .ageRating(AgeRating.R15)
                    .allowBranching(false)
                    .build();

            // when
            NovelResponse created = novelService.create(author.getId(), request);
            em.flush();
            em.clear();

            NovelResponse detail = novelService.getDetail(created.getId());

            // then
            assertThat(detail.getTitle()).isEqualTo("상세조회 테스트");
            assertThat(detail.getGenre()).isEqualTo(Genre.ROMANCE);
            assertThat(detail.getStatus()).isEqualTo(NovelStatus.ONGOING);
            assertThat(detail.getAuthor().getId()).isEqualTo(author.getId());
        }
    }

    @Nested
    @DisplayName("소설 필터링 플로우")
    class FilteringFlow {

        @Test
        @DisplayName("장르별 필터링이 정상 동작해야 함")
        void filterByGenre() {
            // given
            createNovel("판타지 소설", Genre.FANTASY);
            createNovel("로맨스 소설", Genre.ROMANCE);
            em.flush();
            em.clear();

            // when
            Page<NovelSummaryResponse> fantasyNovels = novelService.getList(
                    Genre.FANTASY, null, PageRequest.of(0, 10));

            // then
            assertThat(fantasyNovels.getContent())
                    .extracting(NovelSummaryResponse::getGenre)
                    .containsOnly(Genre.FANTASY);
        }

        private void createNovel(String title, Genre genre) {
            NovelCreateRequest request = NovelCreateRequest.builder()
                    .title(title)
                    .description("설명")
                    .genre(genre)
                    .ageRating(AgeRating.ALL)
                    .allowBranching(true)
                    .build();
            novelService.create(author.getId(), request);
        }
    }
}
