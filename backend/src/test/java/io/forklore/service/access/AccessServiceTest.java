package io.forklore.service.access;

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
import io.forklore.domain.purchase.Purchase;
import io.forklore.domain.purchase.PurchaseRepository;
import io.forklore.domain.subscription.PlanType;
import io.forklore.domain.subscription.Subscription;
import io.forklore.domain.subscription.SubscriptionRepository;
import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.repository.UserRepository;
import jakarta.persistence.EntityManager;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@Transactional
@ActiveProfiles("common")
class AccessServiceTest {

    @Autowired
    private AccessService accessService;

    @Autowired
    private ChapterRepository chapterRepository;

    @Autowired
    private BranchRepository branchRepository;

    @Autowired
    private NovelRepository novelRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private SubscriptionRepository subscriptionRepository;

    @Autowired
    private PurchaseRepository purchaseRepository;

    @Autowired
    private EntityManager em;

    private User author;
    private User reader;
    private User subscriber;
    private Novel novel;
    private Branch branch;
    private Chapter freeChapter;
    private Chapter paidChapter;

    @BeforeEach
    void setUp() {
        author = User.builder()
                .email("access-author@example.com")
                .password("password")
                .nickname("작가")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(author);

        reader = User.builder()
                .email("access-reader@example.com")
                .password("password")
                .nickname("독자")
                .role(UserRole.READER)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(reader);

        subscriber = User.builder()
                .email("access-subscriber@example.com")
                .password("password")
                .nickname("구독자")
                .role(UserRole.READER)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(subscriber);

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

        // 무료 회차
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

        // 유료 회차
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
    @DisplayName("무료 회차 접근 가능")
    void canAccessFreeChapter() {
        // when
        boolean canAccess = accessService.canAccessChapter(reader.getId(), freeChapter.getId());

        // then
        assertThat(canAccess).isTrue();
    }

    @Test
    @DisplayName("비로그인 사용자도 무료 회차 접근 가능")
    void anonymousCanAccessFreeChapter() {
        // when
        boolean canAccess = accessService.canAccessChapter(null, freeChapter.getId());

        // then
        assertThat(canAccess).isTrue();
    }

    @Test
    @DisplayName("비로그인 사용자 유료 회차 접근 불가")
    void anonymousCannotAccessPaidChapter() {
        // when
        boolean canAccess = accessService.canAccessChapter(null, paidChapter.getId());

        // then
        assertThat(canAccess).isFalse();
    }

    @Test
    @DisplayName("구독이 없는 사용자 유료 회차 접근 불가")
    void nonSubscriberCannotAccessPaidChapter() {
        // when
        boolean canAccess = accessService.canAccessChapter(reader.getId(), paidChapter.getId());

        // then
        assertThat(canAccess).isFalse();
    }

    @Test
    @DisplayName("구독자 유료 회차 접근 가능")
    void subscriberCanAccessPaidChapter() {
        // given
        subscriptionRepository.save(Subscription.builder()
                .user(subscriber)
                .planType(PlanType.MONTHLY)
                .autoRenew(true)
                .build());
        em.flush();
        em.clear();

        // when
        boolean canAccess = accessService.canAccessChapter(subscriber.getId(), paidChapter.getId());

        // then
        assertThat(canAccess).isTrue();
    }

    @Test
    @DisplayName("구매한 사용자 유료 회차 접근 가능")
    void purchaserCanAccessPaidChapter() {
        // given
        purchaseRepository.save(Purchase.builder()
                .user(reader)
                .chapter(paidChapter)
                .price(BigDecimal.valueOf(100))
                .build());
        em.flush();
        em.clear();

        // when
        boolean canAccess = accessService.canAccessChapter(reader.getId(), paidChapter.getId());

        // then
        assertThat(canAccess).isTrue();
    }

    @Test
    @DisplayName("접근 결과 상세 - 구독 필요")
    void checkAccessDenied() {
        // when
        AccessService.AccessResult result = accessService.checkAccess(reader.getId(), paidChapter.getId());

        // then
        assertThat(result.allowed()).isFalse();
        assertThat(result.reason()).contains("구독 또는 개별 구매");
        assertThat(result.requiredPrice()).isEqualTo(100);
    }
}
