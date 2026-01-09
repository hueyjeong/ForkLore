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
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;

@ExtendWith(MockitoExtension.class)
class SubscriptionServiceTest {

    @InjectMocks
    private SubscriptionService subscriptionService;

    @Mock
    private SubscriptionRepository subscriptionRepository;

    @Mock
    private UserRepository userRepository;

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
        ReflectionTestUtils.setField(user, "id", 1L);
    }

    @Test
    @DisplayName("월간 구독 생성")
    void subscribeMonthly() {
        // given
        given(userRepository.findById(1L)).willReturn(Optional.of(user));
        given(subscriptionRepository.existsActiveByUserId(any(), any())).willReturn(false);
        given(subscriptionRepository.save(any(Subscription.class))).willAnswer(invocation -> {
            Subscription s = invocation.getArgument(0);
            ReflectionTestUtils.setField(s, "id", 100L);
            return s;
        });

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
        // given
        given(userRepository.findById(1L)).willReturn(Optional.of(user));
        given(subscriptionRepository.existsActiveByUserId(any(), any())).willReturn(false);
        given(subscriptionRepository.save(any(Subscription.class))).willAnswer(invocation -> {
            Subscription s = invocation.getArgument(0);
            ReflectionTestUtils.setField(s, "id", 101L);
            return s;
        });

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
        given(userRepository.findById(1L)).willReturn(Optional.of(user));
        given(subscriptionRepository.existsActiveByUserId(any(), any())).willReturn(true);

        // when & then
        assertThatThrownBy(() -> subscriptionService.subscribe(user.getId(), PlanType.MONTHLY, true))
                .isInstanceOf(IllegalStateException.class)
                .hasMessageContaining("이미 활성화된 구독");
    }

    @Test
    @DisplayName("구독 취소")
    void cancel() {
        // given
        Subscription subscription = Subscription.builder()
                .user(user)
                .planType(PlanType.MONTHLY)
                .autoRenew(true)
                .build();
        given(subscriptionRepository.findActiveByUserId(1L)).willReturn(Optional.of(subscription));

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
        Subscription subscription = Subscription.builder()
                .user(user)
                .planType(PlanType.MONTHLY)
                .autoRenew(true)
                .build();
        given(subscriptionRepository.findActiveByUserId(1L)).willReturn(Optional.of(subscription));

        // when
        SubscriptionResponse response = subscriptionService.changePlan(user.getId(), PlanType.YEARLY);

        // then
        assertThat(response.getPlanType()).isEqualTo(PlanType.YEARLY);
    }

    @Test
    @DisplayName("구독 상태 조회")
    void getStatus() {
        // given
        Subscription subscription = Subscription.builder()
                .user(user)
                .planType(PlanType.MONTHLY)
                .autoRenew(true)
                .build();
        given(subscriptionRepository.findActiveByUserId(1L)).willReturn(Optional.of(subscription));

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
        given(subscriptionRepository.existsActiveByUserId(any(), any())).willReturn(false);
        assertThat(subscriptionService.hasActiveSubscription(user.getId())).isFalse();

        // after subscribing
        given(subscriptionRepository.existsActiveByUserId(any(), any())).willReturn(true);
        assertThat(subscriptionService.hasActiveSubscription(user.getId())).isTrue();
    }
}
