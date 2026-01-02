package io.forklore.service.access;

import io.forklore.domain.branch.Branch;
import io.forklore.domain.chapter.AccessType;
import io.forklore.domain.chapter.Chapter;
import io.forklore.domain.chapter.ChapterRepository;
import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.purchase.PurchaseRepository;
import io.forklore.domain.subscription.SubscriptionRepository;
import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.LocalDate;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;

@ExtendWith(MockitoExtension.class)
class AccessServiceTest {

    @InjectMocks
    private AccessService accessService;

    @Mock
    private ChapterRepository chapterRepository;

    @Mock
    private SubscriptionRepository subscriptionRepository;

    @Mock
    private PurchaseRepository purchaseRepository;

    @Mock
    private UserRepository userRepository;

    private User reader;
    private User subscriber;
    private Chapter freeChapter;
    private Chapter paidChapter;

    @BeforeEach
    void setUp() {
        User author = User.builder()
                .email("access-author@example.com")
                .password("password")
                .nickname("작가")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        ReflectionTestUtils.setField(author, "id", 1L);

        reader = User.builder()
                .email("access-reader@example.com")
                .password("password")
                .nickname("독자")
                .role(UserRole.READER)
                .authProvider(AuthProvider.LOCAL)
                .build();
        ReflectionTestUtils.setField(reader, "id", 2L);

        subscriber = User.builder()
                .email("access-subscriber@example.com")
                .password("password")
                .nickname("구독자")
                .role(UserRole.READER)
                .authProvider(AuthProvider.LOCAL)
                .build();
        ReflectionTestUtils.setField(subscriber, "id", 3L);

        Novel novel = Novel.builder()
                .author(author)
                .title("테스트 소설")
                .genre(Genre.FANTASY)
                .ageRating(AgeRating.ALL)
                .allowBranching(true)
                .build();
        ReflectionTestUtils.setField(novel, "id", 10L);

        Branch branch = Branch.builder()
                .novel(novel)
                .author(author)
                .isMain(true)
                .name("메인 브랜치")
                .build();
        ReflectionTestUtils.setField(branch, "id", 100L);

        // 무료 회차
        freeChapter = Chapter.builder()
                .branch(branch)
                .chapterNumber(1)
                .title("무료 1화")
                .accessType(AccessType.FREE)
                .price(0)
                .build();
        ReflectionTestUtils.setField(freeChapter, "id", 1000L);

        // 유료 회차
        paidChapter = Chapter.builder()
                .branch(branch)
                .chapterNumber(2)
                .title("유료 2화")
                .accessType(AccessType.SUBSCRIPTION)
                .price(100)
                .build();
        ReflectionTestUtils.setField(paidChapter, "id", 1001L);
    }

    @Test
    @DisplayName("무료 회차 접근 가능")
    void canAccessFreeChapter() {
        // given
        given(chapterRepository.findById(1000L)).willReturn(Optional.of(freeChapter));

        // when
        boolean canAccess = accessService.canAccessChapter(reader.getId(), freeChapter.getId());

        // then
        assertThat(canAccess).isTrue();
    }

    @Test
    @DisplayName("비로그인 사용자도 무료 회차 접근 가능")
    void anonymousCanAccessFreeChapter() {
        // given
        given(chapterRepository.findById(1000L)).willReturn(Optional.of(freeChapter));

        // when
        boolean canAccess = accessService.canAccessChapter(null, freeChapter.getId());

        // then
        assertThat(canAccess).isTrue();
    }

    @Test
    @DisplayName("비로그인 사용자 유료 회차 접근 불가")
    void anonymousCannotAccessPaidChapter() {
        // given
        given(chapterRepository.findById(1001L)).willReturn(Optional.of(paidChapter));

        // when
        boolean canAccess = accessService.canAccessChapter(null, paidChapter.getId());

        // then
        assertThat(canAccess).isFalse();
    }

    @Test
    @DisplayName("구독이 없는 사용자 유료 회차 접근 불가")
    void nonSubscriberCannotAccessPaidChapter() {
        // given
        given(chapterRepository.findById(1001L)).willReturn(Optional.of(paidChapter));
        given(purchaseRepository.existsByUserIdAndChapterId(reader.getId(), 1001L)).willReturn(false);
        given(subscriptionRepository.existsActiveByUserId(eq(reader.getId()), any(LocalDate.class))).willReturn(false);

        // when
        boolean canAccess = accessService.canAccessChapter(reader.getId(), paidChapter.getId());

        // then
        assertThat(canAccess).isFalse();
    }

    @Test
    @DisplayName("구독자 유료 회차 접근 가능")
    void subscriberCanAccessPaidChapter() {
        // given
        given(chapterRepository.findById(1001L)).willReturn(Optional.of(paidChapter));
        given(purchaseRepository.existsByUserIdAndChapterId(subscriber.getId(), 1001L)).willReturn(false);
        given(subscriptionRepository.existsActiveByUserId(eq(subscriber.getId()), any(LocalDate.class)))
                .willReturn(true);

        // when
        boolean canAccess = accessService.canAccessChapter(subscriber.getId(), paidChapter.getId());

        // then
        assertThat(canAccess).isTrue();
    }

    @Test
    @DisplayName("구매한 사용자 유료 회차 접근 가능")
    void purchaserCanAccessPaidChapter() {
        // given
        given(chapterRepository.findById(1001L)).willReturn(Optional.of(paidChapter));
        given(purchaseRepository.existsByUserIdAndChapterId(reader.getId(), 1001L)).willReturn(true);

        // when
        boolean canAccess = accessService.canAccessChapter(reader.getId(), paidChapter.getId());

        // then
        assertThat(canAccess).isTrue();
    }

    @Test
    @DisplayName("접근 결과 상세 - 구독 필요")
    void checkAccessDenied() {
        // given
        given(chapterRepository.findById(1001L)).willReturn(Optional.of(paidChapter));
        given(purchaseRepository.existsByUserIdAndChapterId(reader.getId(), 1001L)).willReturn(false);
        given(subscriptionRepository.existsActiveByUserId(eq(reader.getId()), any(LocalDate.class))).willReturn(false);

        // when
        AccessService.AccessResult result = accessService.checkAccess(reader.getId(), paidChapter.getId());

        // then
        assertThat(result.isAllowed()).isFalse();
        assertThat(result.reason()).contains("구독 또는 개별 구매");
        assertThat(result.requiredPrice()).isEqualTo(100);
    }
}
