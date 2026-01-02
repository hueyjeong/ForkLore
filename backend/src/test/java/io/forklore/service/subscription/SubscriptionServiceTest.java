package io.forklore.service.subscription;

import io.forklore.domain.subscription.PlanType;
import io.forklore.domain.subscription.Subscription;
import io.forklore.domain.subscription.SubscriptionRepository;
import io.forklore.domain.subscription.SubscriptionStatus;
import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.dto.response.SubscriptionResponse;
import io.forklore.repository.UserRepository;
import jakarta.persistence.EntityManager;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

@SpringBootTest
@Transactional
@ActiveProfiles("common")
class SubscriptionServiceTest {

    @Autowired
    private SubscriptionService subscriptionService;

    @Autowired
    private SubscriptionRepository subscriptionRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private EntityManager em;

    private User user;

    @BeforeEach
    void setUp() {
        user = User.builder()
                .email("subscriber@example.com")
                .password("password")
                .nickname("구독자")
                .role(UserRole.READER)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(user);
    }

    @Test
    @DisplayName("월간 구독 생성")
    void subscribeMonthly() {
        // when
        SubscriptionResponse response = subscriptionService.subscribe(
                user.getId(), PlanType.MONTHLY, true);

        // then
        assertThat(response.getPlanType()).isEqualTo(PlanType.MONTHLY);
        assertThat(response.getStatus()).isEqualTo(SubscriptionStatus.ACTIVE);
        assertThat(response.isAutoRenew()).isTrue();
        assertThat(response.getEndDate()).isEqualTo(LocalDate.now().plusDays(30));
    }

    @Test
    @DisplayName("연간 구독 생성")
    void subscribeYearly() {
        // when
        SubscriptionResponse response = subscriptionService.subscribe(
                user.getId(), PlanType.YEARLY, false);

        // then
        assertThat(response.getPlanType()).isEqualTo(PlanType.YEARLY);
        assertThat(response.getEndDate()).isEqualTo(LocalDate.now().plusDays(365));
    }

    @Test
    @DisplayName("중복 구독 방지")
    void preventDuplicateSubscription() {
        // given
        subscriptionService.subscribe(user.getId(), PlanType.MONTHLY, true);

        // when & then
        assertThatThrownBy(() -> subscriptionService.subscribe(user.getId(), PlanType.MONTHLY, true))
                .isInstanceOf(IllegalStateException.class)
                .hasMessageContaining("이미 활성화된 구독");
    }

    @Test
    @DisplayName("구독 취소")
    void cancel() {
        // given
        subscriptionService.subscribe(user.getId(), PlanType.MONTHLY, true);
        em.flush();
        em.clear();

        // when
        SubscriptionResponse response = subscriptionService.cancel(user.getId());

        // then
        assertThat(response.getStatus()).isEqualTo(SubscriptionStatus.CANCELLED);
        assertThat(response.isAutoRenew()).isFalse();
    }

    @Test
    @DisplayName("요금제 변경")
    void changePlan() {
        // given
        subscriptionService.subscribe(user.getId(), PlanType.MONTHLY, true);
        em.flush();
        em.clear();

        // when
        SubscriptionResponse response = subscriptionService.changePlan(user.getId(), PlanType.YEARLY);

        // then
        assertThat(response.getPlanType()).isEqualTo(PlanType.YEARLY);
    }

    @Test
    @DisplayName("구독 상태 조회")
    void getStatus() {
        // given
        subscriptionService.subscribe(user.getId(), PlanType.MONTHLY, true);
        em.flush();
        em.clear();

        // when
        Optional<SubscriptionResponse> status = subscriptionService.getStatus(user.getId());

        // then
        assertThat(status).isPresent();
        assertThat(status.get().isActive()).isTrue();
        assertThat(status.get().getRemainingDays()).isLessThanOrEqualTo(30);
    }

    @Test
    @DisplayName("활성 구독 여부 확인")
    void hasActiveSubscription() {
        // initially no subscription
        assertThat(subscriptionService.hasActiveSubscription(user.getId())).isFalse();

        // after subscribing
        subscriptionService.subscribe(user.getId(), PlanType.MONTHLY, true);
        assertThat(subscriptionService.hasActiveSubscription(user.getId())).isTrue();
    }
}
