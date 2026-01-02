package io.forklore.domain.branch;

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
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.test.context.ActiveProfiles;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * @DataJpaTest: 슬라이스 테스트로 빠른 실행 + 자동 롤백
 */
@DataJpaTest
@Import(JpaConfig.class)
@ActiveProfiles("common")
class BranchRepositoryTest {

    @Autowired
    private BranchRepository branchRepository;

    @Autowired
    private TestEntityManager em;

    private User author;
    private Novel novel;

    @BeforeEach
    void setUp() {
        author = User.builder()
                .email("branch-author@example.com")
                .password("password")
                .nickname("브랜치테스트작가")
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
    }

    @Test
    @DisplayName("메인 브랜치 생성 및 조회")
    void createAndFindMainBranch() {
        // given
        Branch mainBranch = Branch.createMainBranch(novel, author);
        em.persist(mainBranch);
        em.flush();
        em.clear();

        // when
        Optional<Branch> found = branchRepository.findByNovelIdAndIsMainTrue(novel.getId());

        // then
        assertThat(found).isPresent();
        assertThat(found.get().isMain()).isTrue();
        assertThat(found.get().getBranchType()).isEqualTo(BranchType.MAIN);
        assertThat(found.get().getVisibility()).isEqualTo(BranchVisibility.PUBLIC);
    }

    @Test
    @DisplayName("파생 브랜치 생성 (포크)")
    void createForkBranch() {
        // given
        Branch mainBranch = Branch.createMainBranch(novel, author);
        em.persist(mainBranch);
        em.flush();
        em.clear();

        User forkAuthor = User.builder()
                .email("fork-author@example.com")
                .password("password")
                .nickname("포크작가")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        em.persist(forkAuthor);

        Branch forkBranch = Branch.builder()
                .novel(novel)
                .author(forkAuthor)
                .isMain(false)
                .parentBranch(mainBranch)
                .forkPointChapter(5)
                .name("IF 스토리: 만약 주인공이...")
                .branchType(BranchType.IF_STORY)
                .visibility(BranchVisibility.PRIVATE)
                .build();
        em.persist(forkBranch);
        em.flush();
        em.clear();

        // when
        Branch found = branchRepository.findById(forkBranch.getId()).orElseThrow();

        // then
        assertThat(found.isMain()).isFalse();
        assertThat(found.getParentBranch().getId()).isEqualTo(mainBranch.getId());
        assertThat(found.getForkPointChapter()).isEqualTo(5);
        assertThat(found.getBranchType()).isEqualTo(BranchType.IF_STORY);
    }

    @Test
    @DisplayName("가시성별 브랜치 목록 조회")
    void findByNovelIdAndVisibility() {
        // given
        Branch mainBranch = Branch.createMainBranch(novel, author);
        em.persist(mainBranch);

        createFanBranch("팬픽1", BranchVisibility.PUBLIC);
        createFanBranch("팬픽2", BranchVisibility.PUBLIC);
        createFanBranch("팬픽3", BranchVisibility.PRIVATE);
        em.flush();
        em.clear();

        // when
        Page<Branch> publicBranches = branchRepository.findByNovelIdAndVisibility(
                novel.getId(), BranchVisibility.PUBLIC, PageRequest.of(0, 10));

        // then
        assertThat(publicBranches.getTotalElements()).isEqualTo(3); // main + 2 public
    }

    @Test
    @DisplayName("공개 브랜치 목록 조회 (PUBLIC + LINKED)")
    void findByNovelIdAndVisibilityIn() {
        // given
        Branch mainBranch = Branch.createMainBranch(novel, author);
        em.persist(mainBranch);

        createFanBranch("팬픽1", BranchVisibility.PUBLIC);
        createFanBranch("팬픽2", BranchVisibility.LINKED);
        createFanBranch("팬픽3", BranchVisibility.PRIVATE);
        em.flush();
        em.clear();

        // when
        Page<Branch> visibleBranches = branchRepository.findByNovelIdAndVisibilityIn(
                novel.getId(),
                List.of(BranchVisibility.PUBLIC, BranchVisibility.LINKED),
                PageRequest.of(0, 10));

        // then
        assertThat(visibleBranches.getTotalElements()).isEqualTo(3); // main + PUBLIC + LINKED
    }

    @Test
    @DisplayName("Soft Delete 확인")
    void softDelete() {
        // given
        Branch branch = createFanBranch("삭제될 브랜치", BranchVisibility.PRIVATE);
        Long branchId = branch.getId();
        em.flush();
        em.clear();

        // when
        Branch found = branchRepository.findById(branchId).orElseThrow();
        found.setDeletedAt(LocalDateTime.now());
        em.persist(found);
        em.flush();
        em.clear();

        // then
        assertThat(branchRepository.findById(branchId)).isEmpty();
    }

    private Branch createFanBranch(String name, BranchVisibility visibility) {
        Branch branch = Branch.builder()
                .novel(novel)
                .author(author)
                .isMain(false)
                .name(name)
                .branchType(BranchType.FAN_FIC)
                .visibility(visibility)
                .build();
        em.persist(branch);
        return branch;
    }
}
