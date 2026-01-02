package io.forklore.domain.chapter;

import io.forklore.domain.branch.Branch;
import io.forklore.domain.branch.BranchType;
import io.forklore.domain.branch.BranchVisibility;
import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.global.config.JpaConfig;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.boot.jpa.test.autoconfigure.TestEntityManager;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ActiveProfiles;

import java.time.LocalDateTime;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * @DataJpaTest: 슬라이스 테스트로 빠른 실행 + 자동 롤백
 */
@DataJpaTest
@Import(JpaConfig.class)
@ActiveProfiles("common")
class ChapterRepositoryTest {

    @Autowired
    private ChapterRepository chapterRepository;

    @Autowired
    private TestEntityManager em;

    private User author;
    private Novel novel;
    private Branch branch;

    @BeforeEach
    void setUp() {
        author = User.builder()
                .email("chapter-author@example.com")
                .password("password")
                .nickname("회차테스트작가")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        em.persist(author);

        novel = Novel.builder()
                .author(author)
                .title("테스트 소설")
                .genre(Genre.FANTASY)
                .ageRating(AgeRating.ALL)
                .allowBranching(true)
                .build();
        em.persist(novel);

        branch = Branch.builder()
                .novel(novel)
                .author(author)
                .isMain(true)
                .name("메인 브랜치")
                .branchType(BranchType.MAIN)
                .visibility(BranchVisibility.PUBLIC)
                .build();
        em.persist(branch);
    }

    @Test
    @DisplayName("회차 생성 및 조회")
    void createAndFind() {
        // given
        Chapter chapter = createChapter("1화. 시작", 1);
        em.flush();
        em.clear();

        // when
        Chapter found = chapterRepository.findById(chapter.getId()).orElseThrow();

        // then
        assertThat(found.getTitle()).isEqualTo("1화. 시작");
        assertThat(found.getChapterNumber()).isEqualTo(1);
        assertThat(found.getStatus()).isEqualTo(ChapterStatus.DRAFT);
    }

    @Test
    @DisplayName("브랜치의 회차 목록 조회 (번호 순)")
    void findByBranchOrdered() {
        // given
        createChapter("3화", 3);
        createChapter("1화", 1);
        createChapter("2화", 2);
        em.flush();
        em.clear();

        // when
        List<Chapter> chapters = chapterRepository.findByBranchIdOrderByChapterNumberAsc(branch.getId());

        // then
        assertThat(chapters).hasSize(3);
        assertThat(chapters.get(0).getChapterNumber()).isEqualTo(1);
        assertThat(chapters.get(1).getChapterNumber()).isEqualTo(2);
        assertThat(chapters.get(2).getChapterNumber()).isEqualTo(3);
    }

    @Test
    @DisplayName("발행된 회차만 조회")
    void findPublishedOnly() {
        // given
        Chapter ch1 = createChapter("1화", 1);
        ch1.publish();
        Chapter ch2 = createChapter("2화", 2);
        ch2.publish();
        createChapter("3화 (초안)", 3);
        em.flush();
        em.clear();

        // when
        List<Chapter> published = chapterRepository.findByBranchIdAndStatusOrderByChapterNumberAsc(
                branch.getId(), ChapterStatus.PUBLISHED);

        // then
        assertThat(published).hasSize(2);
    }

    @Test
    @DisplayName("마지막 회차 번호 조회")
    void findLastChapterNumber() {
        // given
        createChapter("1화", 1);
        createChapter("2화", 2);
        createChapter("3화", 3);
        em.flush();
        em.clear();

        // when
        Chapter lastChapter = chapterRepository.findTopByBranchIdOrderByChapterNumberDesc(branch.getId())
                .orElseThrow();

        // then
        assertThat(lastChapter.getChapterNumber()).isEqualTo(3);
    }

    @Test
    @DisplayName("예약 발행 대상 조회")
    void findScheduledForPublish() {
        // given
        Chapter scheduled = createChapter("예약 회차", 1);
        scheduled.schedule(LocalDateTime.now().minusMinutes(5)); // 5분 전 예약

        Chapter futureScheduled = createChapter("미래 예약", 2);
        futureScheduled.schedule(LocalDateTime.now().plusHours(1)); // 1시간 후 예약
        em.flush();
        em.clear();

        // when
        List<Chapter> toPublish = chapterRepository.findScheduledForPublish(LocalDateTime.now());

        // then
        assertThat(toPublish).hasSize(1);
        assertThat(toPublish.get(0).getTitle()).isEqualTo("예약 회차");
    }

    private Chapter createChapter(String title, int number) {
        Chapter chapter = Chapter.builder()
                .branch(branch)
                .chapterNumber(number)
                .title(title)
                .content("테스트 본문")
                .contentHtml("<p>테스트 본문</p>")
                .wordCount(10)
                .accessType(AccessType.FREE)
                .price(0)
                .build();
        em.persist(chapter);
        return chapter;
    }
}
