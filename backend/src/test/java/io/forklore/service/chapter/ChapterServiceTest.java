package io.forklore.service.chapter;

import io.forklore.domain.branch.Branch;
import io.forklore.domain.branch.BranchRepository;
import io.forklore.domain.branch.BranchType;
import io.forklore.domain.branch.BranchVisibility;
import io.forklore.domain.chapter.AccessType;
import io.forklore.domain.chapter.Chapter;
import io.forklore.domain.chapter.ChapterRepository;
import io.forklore.domain.chapter.ChapterStatus;
import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.novel.NovelRepository;
import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.dto.request.ChapterCreateRequest;
import io.forklore.dto.request.ChapterUpdateRequest;
import io.forklore.dto.response.ChapterResponse;
import io.forklore.dto.response.ChapterSummaryResponse;
import io.forklore.global.error.UnauthorizedException;
import io.forklore.repository.UserRepository;
import jakarta.persistence.EntityManager;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

@SpringBootTest
@Transactional
@ActiveProfiles("common")
class ChapterServiceTest {

    @Autowired
    private ChapterService chapterService;

    @Autowired
    private ChapterRepository chapterRepository;

    @Autowired
    private BranchRepository branchRepository;

    @Autowired
    private NovelRepository novelRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private EntityManager em;

    private User author;
    private User otherUser;
    private Novel novel;
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
        userRepository.save(author);

        otherUser = User.builder()
                .email("other-user@example.com")
                .password("password")
                .nickname("다른사용자")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(otherUser);

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

        // when
        ChapterResponse response = chapterService.create(branch.getId(), author.getId(), request);

        // then
        assertThat(response.getTitle()).isEqualTo("1화. 시작");
        assertThat(response.getChapterNumber()).isEqualTo(1);
        assertThat(response.getStatus()).isEqualTo(ChapterStatus.DRAFT);
        assertThat(response.getContentHtml()).contains("<h1>프롤로그</h1>");
        assertThat(response.getContentHtml()).contains("<strong>테스트</strong>");
    }

    @Test
    @DisplayName("회차 번호 자동 증가")
    void autoIncrementChapterNumber() {
        // given
        createTestChapter("1화");
        createTestChapter("2화");

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
        ChapterResponse created = createTestChapter("원래 제목");
        em.flush();
        em.clear();

        ChapterUpdateRequest request = ChapterUpdateRequest.builder()
                .title("새 제목")
                .content("새 본문")
                .build();

        // when
        ChapterResponse updated = chapterService.update(created.getId(), author.getId(), request);

        // then
        assertThat(updated.getTitle()).isEqualTo("새 제목");
        assertThat(updated.getContent()).isEqualTo("새 본문");
    }

    @Test
    @DisplayName("권한 없는 사용자 수정 시도 실패")
    void updateUnauthorized() {
        // given
        ChapterResponse created = createTestChapter("테스트");
        em.flush();
        em.clear();

        ChapterUpdateRequest request = ChapterUpdateRequest.builder()
                .title("해킹 시도")
                .build();

        // when & then
        assertThatThrownBy(() -> chapterService.update(created.getId(), otherUser.getId(), request))
                .isInstanceOf(UnauthorizedException.class);
    }

    @Test
    @DisplayName("회차 발행")
    void publish() {
        // given
        ChapterResponse created = createTestChapter("발행 테스트");
        em.flush();
        em.clear();

        // when
        ChapterResponse published = chapterService.publish(created.getId(), author.getId());

        // then
        assertThat(published.getStatus()).isEqualTo(ChapterStatus.PUBLISHED);
        assertThat(published.getPublishedAt()).isNotNull();
    }

    @Test
    @DisplayName("회차 예약 발행")
    void schedule() {
        // given
        ChapterResponse created = createTestChapter("예약 테스트");
        LocalDateTime scheduledTime = LocalDateTime.now().plusHours(1);
        em.flush();
        em.clear();

        // when
        ChapterResponse scheduled = chapterService.schedule(created.getId(), author.getId(), scheduledTime);

        // then
        assertThat(scheduled.getStatus()).isEqualTo(ChapterStatus.SCHEDULED);
        assertThat(scheduled.getScheduledAt()).isNotNull();
    }

    @Test
    @DisplayName("과거 시간 예약 실패")
    void schedulePastTime() {
        // given
        ChapterResponse created = createTestChapter("과거 예약");
        LocalDateTime pastTime = LocalDateTime.now().minusHours(1);
        em.flush();
        em.clear();

        // when & then
        assertThatThrownBy(() -> chapterService.schedule(created.getId(), author.getId(), pastTime))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("현재 시간 이후");
    }

    @Test
    @DisplayName("목차 조회")
    void getList() {
        // given
        ChapterResponse ch1 = createTestChapter("1화");
        chapterService.publish(ch1.getId(), author.getId());
        ChapterResponse ch2 = createTestChapter("2화");
        chapterService.publish(ch2.getId(), author.getId());
        createTestChapter("3화 (초안)");
        em.flush();
        em.clear();

        // when
        List<ChapterSummaryResponse> publishedOnly = chapterService.getList(branch.getId(), true);
        List<ChapterSummaryResponse> all = chapterService.getList(branch.getId(), false);

        // then
        assertThat(publishedOnly).hasSize(2);
        assertThat(all).hasSize(3);
    }

    private ChapterResponse createTestChapter(String title) {
        ChapterCreateRequest request = ChapterCreateRequest.builder()
                .title(title)
                .content("테스트 본문")
                .accessType(AccessType.FREE)
                .build();
        return chapterService.create(branch.getId(), author.getId(), request);
    }
}
