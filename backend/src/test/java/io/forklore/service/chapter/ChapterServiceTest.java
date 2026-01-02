package io.forklore.service.chapter;

import io.forklore.domain.branch.Branch;
import io.forklore.domain.branch.BranchRepository;
import io.forklore.domain.chapter.AccessType;
import io.forklore.domain.chapter.Chapter;
import io.forklore.domain.chapter.ChapterRepository;
import io.forklore.domain.chapter.ChapterStatus;
import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.dto.request.ChapterCreateRequest;
import io.forklore.dto.request.ChapterUpdateRequest;
import io.forklore.dto.response.ChapterResponse;
import io.forklore.dto.response.ChapterSummaryResponse;
import io.forklore.global.error.UnauthorizedException;
import io.forklore.util.MarkdownParser;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.BDDMockito.given;

@ExtendWith(MockitoExtension.class)
class ChapterServiceTest {

    @InjectMocks
    private ChapterService chapterService;

    @Mock
    private ChapterRepository chapterRepository;

    @Mock
    private BranchRepository branchRepository;

    @Mock
    private MarkdownParser markdownParser;

    private User author;
    private User otherUser;
    private Branch branch;

    @BeforeEach
    void setUp() {
        author = User.builder()
                .email("service-author@example.com")
                .password("password")
                .nickname("서비스테스트작가")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        ReflectionTestUtils.setField(author, "id", 1L);

        otherUser = User.builder()
                .email("other-user@example.com")
                .password("password")
                .nickname("다른사용자")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        ReflectionTestUtils.setField(otherUser, "id", 2L);

        Novel novel = Novel.builder()
                .author(author)
                .title("테스트 소설")
                .genre(Genre.FANTASY)
                .ageRating(AgeRating.ALL)
                .allowBranching(true)
                .build();
        ReflectionTestUtils.setField(novel, "id", 10L);

        branch = Branch.builder()
                .novel(novel)
                .author(author)
                .isMain(true)
                .name("메인 브랜치")
                .build();
        ReflectionTestUtils.setField(branch, "id", 100L);
    }

    @Test
    @DisplayName("회차 생성")
    void create() {
        // given
        ChapterCreateRequest request = ChapterCreateRequest.builder()
                .title("1화. 시작")
                .content("# 프롤로그\n\n이것은 **테스트** 소설입니다.")
                .accessType(AccessType.FREE)
                .authorComment("첫 회차입니다!")
                .build();

        given(branchRepository.findById(100L)).willReturn(Optional.of(branch));
        given(chapterRepository.findTopByBranchIdOrderByChapterNumberDesc(100L)).willReturn(Optional.empty());
        given(markdownParser.toHtml(anyString())).willReturn("<h1>프롤로그</h1><p>이것은 <strong>테스트</strong> 소설입니다.</p>");
        given(markdownParser.countWords(anyString())).willReturn(10);
        given(chapterRepository.save(any(Chapter.class))).willAnswer(invocation -> {
            Chapter c = invocation.getArgument(0);
            ReflectionTestUtils.setField(c, "id", 1000L);
            return c;
        });

        // when
        ChapterResponse response = chapterService.create(branch.getId(), author.getId(), request);

        // then
        assertThat(response.getTitle()).isEqualTo("1화. 시작");
        assertThat(response.getChapterNumber()).isEqualTo(1);
        assertThat(response.getContentHtml()).contains("<h1>프롤로그</h1>");
    }

    @Test
    @DisplayName("회차 번호 자동 증가")
    void autoIncrementChapterNumber() {
        // given
        Chapter existing = Chapter.builder().chapterNumber(2).build();
        given(branchRepository.findById(100L)).willReturn(Optional.of(branch));
        given(chapterRepository.findTopByBranchIdOrderByChapterNumberDesc(100L)).willReturn(Optional.of(existing));
        given(chapterRepository.save(any(Chapter.class))).willAnswer(invocation -> invocation.getArgument(0));

        ChapterCreateRequest request = ChapterCreateRequest.builder()
                .title("3화")
                .content("본문")
                .build();

        // when
        ChapterResponse response = chapterService.create(branch.getId(), author.getId(), request);

        // then
        assertThat(response.getChapterNumber()).isEqualTo(3);
    }

    @Test
    @DisplayName("회차 수정")
    void update() {
        // given
        Chapter chapter = Chapter.builder()
                .branch(branch)
                .chapterNumber(1)
                .title("원래 제목")
                .content("원래 본문")
                .build();
        ReflectionTestUtils.setField(chapter, "id", 1000L);

        given(chapterRepository.findById(1000L)).willReturn(Optional.of(chapter));
        given(markdownParser.toHtml("새 본문")).willReturn("<p>새 본문</p>");
        given(markdownParser.countWords("새 본문")).willReturn(5);

        ChapterUpdateRequest request = ChapterUpdateRequest.builder()
                .title("새 제목")
                .content("새 본문")
                .build();

        // when
        ChapterResponse updated = chapterService.update(chapter.getId(), author.getId(), request);

        // then
        assertThat(updated.getTitle()).isEqualTo("새 제목");
        assertThat(updated.getContent()).isEqualTo("새 본문");
    }

    @Test
    @DisplayName("권한 없는 사용자 수정 시도 실패")
    void updateUnauthorized() {
        // given
        Chapter chapter = Chapter.builder()
                .branch(branch)
                .build();
        ReflectionTestUtils.setField(chapter, "id", 1000L);
        given(chapterRepository.findById(1000L)).willReturn(Optional.of(chapter));

        ChapterUpdateRequest request = ChapterUpdateRequest.builder()
                .title("해킹 시도")
                .build();

        // when & then
        assertThatThrownBy(() -> chapterService.update(chapter.getId(), otherUser.getId(), request))
                .isInstanceOf(UnauthorizedException.class);
    }

    @Test
    @DisplayName("회차 발행")
    void publish() {
        // given
        Chapter chapter = Chapter.builder()
                .branch(branch)
                .build();
        ReflectionTestUtils.setField(chapter, "id", 1000L);
        given(chapterRepository.findById(1000L)).willReturn(Optional.of(chapter));

        // when
        ChapterResponse published = chapterService.publish(chapter.getId(), author.getId());

        // then
        assertThat(published.getStatus()).isEqualTo(ChapterStatus.PUBLISHED);
        assertThat(published.getPublishedAt()).isNotNull();
    }

    @Test
    @DisplayName("회차 예약 발행")
    void schedule() {
        // given
        Chapter chapter = Chapter.builder()
                .branch(branch)
                .build();
        ReflectionTestUtils.setField(chapter, "id", 1000L);
        given(chapterRepository.findById(1000L)).willReturn(Optional.of(chapter));
        LocalDateTime scheduledTime = LocalDateTime.now().plusHours(1);

        // when
        ChapterResponse scheduled = chapterService.schedule(chapter.getId(), author.getId(), scheduledTime);

        // then
        assertThat(scheduled.getStatus()).isEqualTo(ChapterStatus.SCHEDULED);
        assertThat(scheduled.getScheduledAt()).isNotNull();
    }

    @Test
    @DisplayName("과거 시간 예약 실패")
    void schedulePastTime() {
        // given
        Chapter chapter = Chapter.builder()
                .branch(branch)
                .build();
        ReflectionTestUtils.setField(chapter, "id", 1000L);
        given(chapterRepository.findById(1000L)).willReturn(Optional.of(chapter));
        LocalDateTime pastTime = LocalDateTime.now().minusHours(1);

        // when & then
        assertThatThrownBy(() -> chapterService.schedule(chapter.getId(), author.getId(), pastTime))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("현재 시간 이후");
    }

    @Test
    @DisplayName("목차 조회")
    void getList() {
        // given
        Chapter ch1 = Chapter.builder().chapterNumber(1).build();
        ReflectionTestUtils.setField(ch1, "status", ChapterStatus.PUBLISHED);

        Chapter ch2 = Chapter.builder().chapterNumber(2).build();
        ReflectionTestUtils.setField(ch2, "status", ChapterStatus.DRAFT);

        given(chapterRepository.findByBranchIdAndStatusOrderByChapterNumberAsc(100L, ChapterStatus.PUBLISHED))
                .willReturn(List.of(ch1));
        given(chapterRepository.findByBranchIdOrderByChapterNumberAsc(100L))
                .willReturn(List.of(ch1, ch2));

        // when
        List<ChapterSummaryResponse> publishedOnly = chapterService.getList(100L, true);
        List<ChapterSummaryResponse> all = chapterService.getList(100L, false);

        // then
        assertThat(publishedOnly).hasSize(1);
        assertThat(all).hasSize(2);
    }
}
