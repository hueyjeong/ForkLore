package io.forklore.security.aop;

import io.forklore.domain.branch.Branch;
import io.forklore.domain.branch.BranchRepository;
import io.forklore.domain.branch.BranchType;
import io.forklore.domain.branch.BranchVisibility;
import io.forklore.domain.chapter.AccessType;
import io.forklore.domain.chapter.Chapter;
import io.forklore.domain.chapter.ChapterRepository;
import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.novel.NovelRepository;
import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@Transactional
@ActiveProfiles("test")
class AccessCheckerTest {

    @Autowired
    private AccessChecker accessChecker;

    @Autowired
    private ChapterRepository chapterRepository;

    @Autowired
    private BranchRepository branchRepository;

    @Autowired
    private NovelRepository novelRepository;

    @Autowired
    private UserRepository userRepository;

    private User author;
    private User reader;
    private Novel novel;
    private Branch branch;
    private Chapter freeChapter;
    private Chapter paidChapter;

    @BeforeEach
    void setUp() {
        author = User.builder()
                .email("aop-author@example.com")
                .password("password")
                .nickname("작가")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(author);

        reader = User.builder()
                .email("aop-reader@example.com")
                .password("password")
                .nickname("독자")
                .role(UserRole.READER)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(reader);

        novel = Novel.builder()
                .author(author)
                .title("테스트 소설")
                .genre(Genre.FANTASY)
                .ageRating(AgeRating.ALL)
                .allowBranching(true)
                .build();
        novelRepository.save(novel);

        branch = Branch.builder()
                .novel(novel)
                .author(author)
                .isMain(true)
                .name("메인 브랜치")
                .branchType(BranchType.MAIN)
                .visibility(BranchVisibility.PUBLIC)
                .build();
        branchRepository.save(branch);

        freeChapter = chapterRepository.save(Chapter.builder()
                .branch(branch)
                .chapterNumber(1)
                .title("무료 1화")
                .content("무료 본문")
                .contentHtml("<p>무료 본문</p>")
                .wordCount(10)
                .accessType(AccessType.FREE)
                .price(0)
                .build());

        paidChapter = chapterRepository.save(Chapter.builder()
                .branch(branch)
                .chapterNumber(2)
                .title("유료 2화")
                .content("유료 본문")
                .contentHtml("<p>유료 본문</p>")
                .wordCount(10)
                .accessType(AccessType.SUBSCRIPTION)
                .price(100)
                .build());
    }

    @Test
    @DisplayName("무료 회차 접근 가능 (비로그인)")
    void freeChapterAccessibleWithoutLogin() {
        boolean canAccess = accessChecker.canAccessChapter(null, freeChapter.getId());
        assertThat(canAccess).isTrue();
    }

    @Test
    @DisplayName("무료 회차 접근 가능 (로그인)")
    void freeChapterAccessibleWithLogin() {
        boolean canAccess = accessChecker.canAccessChapter(reader.getId(), freeChapter.getId());
        assertThat(canAccess).isTrue();
    }

    @Test
    @DisplayName("유료 회차 비로그인 접근 불가")
    void paidChapterNotAccessibleWithoutLogin() {
        boolean canAccess = accessChecker.canAccessChapter(null, paidChapter.getId());
        assertThat(canAccess).isFalse();
    }

    @Test
    @DisplayName("유료 회차 로그인 시 접근 가능 (임시)")
    void paidChapterAccessibleWithLogin() {
        // 현재는 로그인만 하면 접근 가능 (PR 병합 후 구독/구매 로직 추가)
        boolean canAccess = accessChecker.canAccessChapter(reader.getId(), paidChapter.getId());
        assertThat(canAccess).isTrue();
    }
}
