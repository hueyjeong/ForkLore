package io.forklore.service.novel;

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
import io.forklore.dto.response.NovelSummaryResponse;
import io.forklore.global.error.EntityNotFoundException;
import io.forklore.global.error.UnauthorizedException;
import io.forklore.repository.UserRepository;
import jakarta.persistence.EntityManager;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

@SpringBootTest
@Transactional
@ActiveProfiles("common")
class NovelServiceTest {

    @Autowired
    private NovelService novelService;

    @Autowired
    private NovelRepository novelRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private EntityManager em;

    private User author;
    private User otherUser;

    @BeforeEach
    void setUp() {
        author = User.builder()
                .email("author@example.com")
                .password("password")
                .nickname("작가")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(author);

        otherUser = User.builder()
                .email("other@example.com")
                .password("password")
                .nickname("다른사용자")
                .role(UserRole.READER)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(otherUser);
    }

    @Test
    @DisplayName("소설 생성")
    void create_ShouldCreateNovel() {
        // given
        NovelCreateRequest request = NovelCreateRequest.builder()
                .title("테스트 소설")
                .description("테스트 설명")
                .genre(Genre.FANTASY)
                .ageRating(AgeRating.ALL)
                .allowBranching(true)
                .build();

        // when
        NovelResponse response = novelService.create(author.getId(), request);

        // then
        assertThat(response.getId()).isNotNull();
        assertThat(response.getTitle()).isEqualTo("테스트 소설");
        assertThat(response.getAuthor().getNickname()).isEqualTo("작가");
        assertThat(response.getGenre()).isEqualTo(Genre.FANTASY);
        assertThat(response.getStatus()).isEqualTo(NovelStatus.ONGOING);
    }

    @Test
    @DisplayName("소설 목록 조회 - 전체")
    void getList_ShouldReturnPagedNovels() {
        // given
        createTestNovel("소설1", Genre.FANTASY, NovelStatus.ONGOING);
        createTestNovel("소설2", Genre.ROMANCE, NovelStatus.ONGOING);
        em.flush();
        em.clear();

        // when
        Page<NovelSummaryResponse> result = novelService.getList(null, null, PageRequest.of(0, 10));

        // then
        assertThat(result.getTotalElements()).isEqualTo(2);
    }

    @Test
    @DisplayName("소설 목록 조회 - 장르 필터")
    void getList_WithGenreFilter() {
        // given
        createTestNovel("판타지", Genre.FANTASY, NovelStatus.ONGOING);
        createTestNovel("로맨스", Genre.ROMANCE, NovelStatus.ONGOING);
        em.flush();
        em.clear();

        // when
        Page<NovelSummaryResponse> result = novelService.getList(Genre.FANTASY, null, PageRequest.of(0, 10));

        // then
        assertThat(result.getTotalElements()).isEqualTo(1);
        assertThat(result.getContent().get(0).getGenre()).isEqualTo(Genre.FANTASY);
    }

    @Test
    @DisplayName("소설 상세 조회")
    void getDetail_ShouldReturnNovel() {
        // given
        Novel novel = createTestNovel("테스트 소설", Genre.FANTASY, NovelStatus.ONGOING);
        em.flush();
        em.clear();

        // when
        NovelResponse response = novelService.getDetail(novel.getId());

        // then
        assertThat(response.getTitle()).isEqualTo("테스트 소설");
        assertThat(response.getAuthor().getId()).isEqualTo(author.getId());
    }

    @Test
    @DisplayName("존재하지 않는 소설 조회 시 예외")
    void getDetail_ShouldThrowWhenNotFound() {
        // when & then
        assertThatThrownBy(() -> novelService.getDetail(999L))
                .isInstanceOf(EntityNotFoundException.class);
    }

    @Test
    @DisplayName("소설 수정 - 작가 본인")
    void update_ShouldModifyNovel() {
        // given
        Novel novel = createTestNovel("원래 제목", Genre.FANTASY, NovelStatus.ONGOING);
        em.flush();
        em.clear();

        NovelUpdateRequest request = NovelUpdateRequest.builder()
                .title("수정된 제목")
                .status(NovelStatus.COMPLETED)
                .build();

        // when
        NovelResponse response = novelService.update(author.getId(), novel.getId(), request);

        // then
        assertThat(response.getTitle()).isEqualTo("수정된 제목");
        assertThat(response.getStatus()).isEqualTo(NovelStatus.COMPLETED);
    }

    @Test
    @DisplayName("소설 수정 - 다른 사용자가 시도 시 예외")
    void update_ShouldThrowWhenNotAuthor() {
        // given
        Novel novel = createTestNovel("테스트", Genre.FANTASY, NovelStatus.ONGOING);
        em.flush();
        em.clear();

        NovelUpdateRequest request = NovelUpdateRequest.builder()
                .title("수정 시도")
                .build();

        // when & then
        assertThatThrownBy(() -> novelService.update(otherUser.getId(), novel.getId(), request))
                .isInstanceOf(UnauthorizedException.class);
    }

    @Test
    @DisplayName("소설 삭제 - 소프트 삭제")
    void delete_ShouldSoftDelete() {
        // given
        Novel novel = createTestNovel("삭제될 소설", Genre.FANTASY, NovelStatus.ONGOING);
        Long novelId = novel.getId();
        em.flush();
        em.clear();

        // when
        novelService.delete(author.getId(), novelId);
        em.flush();
        em.clear();

        // then - @SQLRestriction으로 인해 조회되지 않아야 함
        assertThat(novelRepository.findById(novelId)).isEmpty();
    }

    @Test
    @DisplayName("소설 삭제 - 다른 사용자가 시도 시 예외")
    void delete_ShouldThrowWhenNotAuthor() {
        // given
        Novel novel = createTestNovel("테스트", Genre.FANTASY, NovelStatus.ONGOING);
        em.flush();
        em.clear();

        // when & then
        assertThatThrownBy(() -> novelService.delete(otherUser.getId(), novel.getId()))
                .isInstanceOf(UnauthorizedException.class);
    }

    private Novel createTestNovel(String title, Genre genre, NovelStatus status) {
        Novel novel = Novel.builder()
                .author(author)
                .title(title)
                .genre(genre)
                .ageRating(AgeRating.ALL)
                .allowBranching(true)
                .build();
        novel.update(null, null, null, null, null, status, null);
        return novelRepository.save(novel);
    }
}
