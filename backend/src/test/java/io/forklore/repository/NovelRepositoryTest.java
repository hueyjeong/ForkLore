package io.forklore.repository;

import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.novel.NovelRepository;
import io.forklore.domain.novel.NovelStatus;
import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import jakarta.persistence.EntityManager;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@Transactional
@ActiveProfiles("common")
class NovelRepositoryTest {

    @Autowired
    private NovelRepository novelRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private EntityManager em;

    private User author;

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
    }

    @Test
    @DisplayName("Novel 저장 및 조회")
    void saveAndFind() {
        // given
        Novel novel = Novel.builder()
                .author(author)
                .title("테스트 소설")
                .description("테스트 설명")
                .genre(Genre.FANTASY)
                .ageRating(AgeRating.ALL)
                .allowBranching(true)
                .build();
        
        // when
        Novel saved = novelRepository.save(novel);
        em.flush();
        em.clear();

        // then
        Novel found = novelRepository.findById(saved.getId()).orElseThrow();
        assertThat(found.getTitle()).isEqualTo("테스트 소설");
        assertThat(found.getGenre()).isEqualTo(Genre.FANTASY);
        assertThat(found.getAuthor().getNickname()).isEqualTo("작가");
    }

    @Test
    @DisplayName("장르별 조회 (페이징)")
    void findByGenre() {
        // given
        createNovel("판타지 소설 1", Genre.FANTASY, NovelStatus.ONGOING);
        createNovel("판타지 소설 2", Genre.FANTASY, NovelStatus.ONGOING);
        createNovel("로맨스 소설", Genre.ROMANCE, NovelStatus.ONGOING);
        em.flush();
        em.clear();

        // when
        Pageable pageable = PageRequest.of(0, 10);
        Page<Novel> result = novelRepository.findByGenre(Genre.FANTASY, pageable);

        // then
        assertThat(result.getTotalElements()).isEqualTo(2);
        assertThat(result.getContent()).allMatch(n -> n.getGenre() == Genre.FANTASY);
    }

    @Test
    @DisplayName("상태별 조회 (페이징)")
    void findByStatus() {
        // given
        createNovel("연재중 소설", Genre.FANTASY, NovelStatus.ONGOING);
        createNovel("완결 소설", Genre.FANTASY, NovelStatus.COMPLETED);
        em.flush();
        em.clear();

        // when
        Pageable pageable = PageRequest.of(0, 10);
        Page<Novel> result = novelRepository.findByStatus(NovelStatus.ONGOING, pageable);

        // then
        assertThat(result.getTotalElements()).isEqualTo(1);
        assertThat(result.getContent().get(0).getTitle()).isEqualTo("연재중 소설");
    }

    @Test
    @DisplayName("작가별 조회 (페이징)")
    void findByAuthorId() {
        // given
        User anotherAuthor = User.builder()
                .email("another@example.com")
                .password("password")
                .nickname("다른작가")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(anotherAuthor);

        createNovel("첫번째 작가 소설", Genre.FANTASY, NovelStatus.ONGOING);
        Novel anotherNovel = Novel.builder()
                .author(anotherAuthor)
                .title("다른 작가 소설")
                .genre(Genre.ROMANCE)
                .ageRating(AgeRating.ALL)
                .build();
        novelRepository.save(anotherNovel);
        em.flush();
        em.clear();

        // when
        Pageable pageable = PageRequest.of(0, 10);
        Page<Novel> result = novelRepository.findByAuthorId(author.getId(), pageable);

        // then
        assertThat(result.getTotalElements()).isEqualTo(1);
        assertThat(result.getContent().get(0).getTitle()).isEqualTo("첫번째 작가 소설");
    }

    @Test
    @DisplayName("장르 + 상태 복합 필터링")
    void findByGenreAndStatus() {
        // given
        createNovel("판타지 연재중", Genre.FANTASY, NovelStatus.ONGOING);
        createNovel("판타지 완결", Genre.FANTASY, NovelStatus.COMPLETED);
        createNovel("로맨스 연재중", Genre.ROMANCE, NovelStatus.ONGOING);
        em.flush();
        em.clear();

        // when
        Pageable pageable = PageRequest.of(0, 10);
        Page<Novel> result = novelRepository.findByGenreAndStatus(Genre.FANTASY, NovelStatus.ONGOING, pageable);

        // then
        assertThat(result.getTotalElements()).isEqualTo(1);
        assertThat(result.getContent().get(0).getTitle()).isEqualTo("판타지 연재중");
    }

    @Test
    @DisplayName("Soft Delete 확인 - @SQLRestriction 동작")
    void softDelete() {
        // given
        Novel novel = createNovel("삭제될 소설", Genre.FANTASY, NovelStatus.ONGOING);
        Long novelId = novel.getId();
        em.flush();
        em.clear();

        // when
        Novel found = novelRepository.findById(novelId).orElseThrow();
        found.setDeletedAt(LocalDateTime.now());
        novelRepository.save(found);
        em.flush();
        em.clear();

        // then
        assertThat(novelRepository.findById(novelId)).isEmpty();
    }

    private Novel createNovel(String title, Genre genre, NovelStatus status) {
        Novel novel = Novel.builder()
                .author(author)
                .title(title)
                .genre(genre)
                .ageRating(AgeRating.ALL)
                .allowBranching(true)
                .build();
        // status 설정
        novel.update(null, null, null, null, null, status, null);
        return novelRepository.save(novel);
    }
}
