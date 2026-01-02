package io.forklore.service.branch;

import io.forklore.domain.branch.*;
import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.novel.NovelRepository;
import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.dto.request.BranchCreateRequest;
import io.forklore.dto.request.BranchUpdateRequest;
import io.forklore.dto.response.BranchResponse;
import io.forklore.dto.response.BranchSummaryResponse;
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
class BranchServiceTest {

    @Autowired
    private BranchService branchService;

    @Autowired
    private BranchRepository branchRepository;

    @Autowired
    private NovelRepository novelRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private EntityManager em;

    private User author;
    private User fanAuthor;
    private Novel novel;

    @BeforeEach
    void setUp() {
        author = User.builder()
                .email("original-author@example.com")
                .password("password")
                .nickname("원작작가")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(author);

        fanAuthor = User.builder()
                .email("fan-author@example.com")
                .password("password")
                .nickname("팬작가")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(fanAuthor);

        novel = Novel.builder()
                .author(author)
                .title("테스트 소설")
                .description("테스트 설명")
                .genre(Genre.FANTASY)
                .ageRating(AgeRating.ALL)
                .allowBranching(true)
                .build();
        novelRepository.save(novel);
    }

    @Test
    @DisplayName("메인 브랜치 생성")
    void createMainBranch() {
        // when
        Branch mainBranch = branchService.createMainBranch(novel, author);
        em.flush();
        em.clear();

        // then
        assertThat(mainBranch.isMain()).isTrue();
        assertThat(mainBranch.getBranchType()).isEqualTo(BranchType.MAIN);
        assertThat(mainBranch.getVisibility()).isEqualTo(BranchVisibility.PUBLIC);
        assertThat(mainBranch.getNovel().getId()).isEqualTo(novel.getId());
    }

    @Test
    @DisplayName("브랜치 포크")
    void fork() {
        // given
        Branch mainBranch = branchService.createMainBranch(novel, author);
        em.flush();
        em.clear();

        BranchCreateRequest request = BranchCreateRequest.builder()
                .parentBranchId(mainBranch.getId())
                .forkPointChapter(10)
                .name("IF: 주인공이 악역이었다면")
                .description("주인공이 악역으로 태어났다면?")
                .branchType(BranchType.IF_STORY)
                .visibility(BranchVisibility.PRIVATE)
                .build();

        // when
        BranchResponse response = branchService.fork(novel.getId(), fanAuthor.getId(), request);

        // then
        assertThat(response.getName()).isEqualTo("IF: 주인공이 악역이었다면");
        assertThat(response.getBranchType()).isEqualTo(BranchType.IF_STORY);
        assertThat(response.isMain()).isFalse();
        assertThat(response.getParentBranchId()).isEqualTo(mainBranch.getId());
    }

    @Test
    @DisplayName("공개 브랜치 목록 조회")
    void getPublicBranchList() {
        // given
        Branch mainBranch = branchService.createMainBranch(novel, author);
        createFanBranch("팬픽1", BranchVisibility.PUBLIC);
        createFanBranch("팬픽2", BranchVisibility.LINKED);
        createFanBranch("팬픽3", BranchVisibility.PRIVATE);
        em.flush();
        em.clear();

        // when
        Page<BranchSummaryResponse> result = branchService.getPublicBranchList(
                novel.getId(), PageRequest.of(0, 10));

        // then
        assertThat(result.getTotalElements()).isEqualTo(3); // main + PUBLIC + LINKED
    }

    @Test
    @DisplayName("브랜치 수정 - 작가 본인만")
    void update() {
        // given
        Branch branch = createFanBranch("원래 이름", BranchVisibility.PRIVATE);
        em.flush();
        em.clear();

        BranchUpdateRequest request = BranchUpdateRequest.builder()
                .name("새 이름")
                .description("새 설명")
                .build();

        // when
        BranchResponse response = branchService.update(fanAuthor.getId(), branch.getId(), request);

        // then
        assertThat(response.getName()).isEqualTo("새 이름");
        assertThat(response.getDescription()).isEqualTo("새 설명");
    }

    @Test
    @DisplayName("브랜치 수정 - 권한 없는 사용자 실패")
    void updateUnauthorized() {
        // given
        Branch branch = createFanBranch("테스트", BranchVisibility.PRIVATE);
        em.flush();
        em.clear();

        BranchUpdateRequest request = BranchUpdateRequest.builder()
                .name("새 이름")
                .build();

        // when & then
        assertThatThrownBy(() -> branchService.update(author.getId(), branch.getId(), request))
                .isInstanceOf(UnauthorizedException.class);
    }

    @Test
    @DisplayName("브랜치 투표")
    void vote() {
        // given
        Branch branch = createFanBranch("인기 팬픽", BranchVisibility.PUBLIC);
        em.flush();
        em.clear();

        // when
        branchService.vote(author.getId(), branch.getId());
        em.flush();
        em.clear();

        // then
        Branch found = branchRepository.findById(branch.getId()).orElseThrow();
        assertThat(found.getVoteCount()).isEqualTo(1);
    }

    @Test
    @DisplayName("중복 투표 방지")
    void duplicateVote() {
        // given
        Branch branch = createFanBranch("인기 팬픽", BranchVisibility.PUBLIC);
        branchService.vote(author.getId(), branch.getId());
        em.flush();
        em.clear();

        // when & then
        assertThatThrownBy(() -> branchService.vote(author.getId(), branch.getId()))
                .isInstanceOf(IllegalStateException.class)
                .hasMessageContaining("이미 투표");
    }

    @Test
    @DisplayName("투표 취소")
    void unvote() {
        // given
        Branch branch = createFanBranch("인기 팬픽", BranchVisibility.PUBLIC);
        branchService.vote(author.getId(), branch.getId());
        em.flush();
        em.clear();

        // when
        branchService.unvote(author.getId(), branch.getId());
        em.flush();
        em.clear();

        // then
        Branch found = branchRepository.findById(branch.getId()).orElseThrow();
        assertThat(found.getVoteCount()).isEqualTo(0);
    }

    private Branch createFanBranch(String name, BranchVisibility visibility) {
        Branch branch = Branch.builder()
                .novel(novel)
                .author(fanAuthor)
                .isMain(false)
                .name(name)
                .branchType(BranchType.FAN_FIC)
                .visibility(visibility)
                .build();
        return branchRepository.save(branch);
    }
}
