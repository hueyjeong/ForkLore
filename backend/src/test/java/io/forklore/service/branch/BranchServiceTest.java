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
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;

@ExtendWith(MockitoExtension.class)
class BranchServiceTest {

    @InjectMocks
    private BranchService branchService;

    @Mock
    private BranchRepository branchRepository;

    @Mock
    private BranchVoteRepository branchVoteRepository;

    @Mock
    private NovelRepository novelRepository;

    @Mock
    private UserRepository userRepository;

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
        ReflectionTestUtils.setField(author, "id", 1L);

        fanAuthor = User.builder()
                .email("fan-author@example.com")
                .password("password")
                .nickname("팬작가")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        ReflectionTestUtils.setField(fanAuthor, "id", 2L);

        novel = Novel.builder()
                .author(author)
                .title("테스트 소설")
                .description("테스트 설명")
                .genre(Genre.FANTASY)
                .ageRating(AgeRating.ALL)
                .allowBranching(true)
                .build();
        ReflectionTestUtils.setField(novel, "id", 10L);
    }

    @Test
    @DisplayName("메인 브랜치 생성")
    void createMainBranch() {
        // given
        given(branchRepository.save(any(Branch.class))).willAnswer(invocation -> invocation.getArgument(0));

        // when
        Branch mainBranch = branchService.createMainBranch(novel, author);

        // then
        assertThat(mainBranch.isMain()).isTrue();
        assertThat(mainBranch.getBranchType()).isEqualTo(BranchType.MAIN);
        assertThat(mainBranch.getNovel().getId()).isEqualTo(novel.getId());
    }

    @Test
    @DisplayName("브랜치 포크")
    void fork() {
        // given
        Branch mainBranch = Branch.builder()
                .novel(novel)
                .author(author)
                .isMain(true)
                .name("메인 브랜치")
                .build();
        ReflectionTestUtils.setField(mainBranch, "id", 100L);

        given(novelRepository.findById(10L)).willReturn(Optional.of(novel));
        given(userRepository.findById(2L)).willReturn(Optional.of(fanAuthor));
        given(branchRepository.findById(100L)).willReturn(Optional.of(mainBranch));
        given(branchRepository.save(any(Branch.class))).willAnswer(invocation -> {
            Branch b = invocation.getArgument(0);
            ReflectionTestUtils.setField(b, "id", 101L);
            return b;
        });

        BranchCreateRequest request = BranchCreateRequest.builder()
                .parentBranchId(100L)
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
        assertThat(response.getParentBranchId()).isEqualTo(100L);
    }

    @Test
    @DisplayName("공개 브랜치 목록 조회")
    void getPublicBranchList() {
        // given
        Branch b1 = Branch.builder()
                .author(fanAuthor)
                .name("팬픽1")
                .visibility(BranchVisibility.PUBLIC)
                .build();
        Page<Branch> page = new PageImpl<>(List.of(b1));
        given(branchRepository.findByNovelIdAndVisibilityIn(any(), any(), any())).willReturn(page);

        // when
        Page<BranchSummaryResponse> result = branchService.getPublicBranchList(
                novel.getId(), PageRequest.of(0, 10));

        // then
        assertThat(result.getTotalElements()).isEqualTo(1);
    }

    @Test
    @DisplayName("브랜치 수정 - 작가 본인만")
    void update() {
        // given
        Branch branch = Branch.builder()
                .novel(novel)
                .author(fanAuthor)
                .name("원래 이름")
                .build();
        ReflectionTestUtils.setField(branch, "id", 101L);

        given(branchRepository.findById(101L)).willReturn(Optional.of(branch));

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
        Branch branch = Branch.builder()
                .author(fanAuthor)
                .build();
        ReflectionTestUtils.setField(branch, "id", 101L);
        given(branchRepository.findById(101L)).willReturn(Optional.of(branch));

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
        Branch branch = Branch.builder()
                .author(fanAuthor)
                .build();
        ReflectionTestUtils.setField(branch, "id", 101L);
        given(branchRepository.findById(101L)).willReturn(Optional.of(branch));
        given(branchVoteRepository.existsByUserIdAndBranchId(author.getId(), 101L)).willReturn(false);

        // when
        branchService.vote(author.getId(), branch.getId());

        // then
        assertThat(branch.getVoteCount()).isEqualTo(1);
    }

    @Test
    @DisplayName("중복 투표 방지")
    void duplicateVote() {
        // given
        Branch branch = Branch.builder()
                .author(fanAuthor)
                .build();
        ReflectionTestUtils.setField(branch, "id", 101L);
        given(branchRepository.findById(101L)).willReturn(Optional.of(branch));
        given(branchVoteRepository.existsByUserIdAndBranchId(author.getId(), 101L)).willReturn(true);

        // when & then
        assertThatThrownBy(() -> branchService.vote(author.getId(), branch.getId()))
                .isInstanceOf(IllegalStateException.class)
                .hasMessageContaining("이미 투표");
    }

    @Test
    @DisplayName("투표 취소")
    void unvote() {
        // given
        Branch branch = Branch.builder()
                .author(fanAuthor)
                .build();
        ReflectionTestUtils.setField(branch, "id", 101L);
        ReflectionTestUtils.setField(branch, "voteCount", 1);
        given(branchRepository.findById(101L)).willReturn(Optional.of(branch));
        given(branchVoteRepository.existsByUserIdAndBranchId(author.getId(), 101L)).willReturn(true);

        // when
        branchService.unvote(author.getId(), branch.getId());

        // then
        assertThat(branch.getVoteCount()).isEqualTo(0);
    }
}
