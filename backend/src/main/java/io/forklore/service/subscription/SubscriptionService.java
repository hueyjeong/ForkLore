package io.forklore.service.subscription;

import io.forklore.domain.subscription.PlanType;
import io.forklore.domain.subscription.Subscription;
import io.forklore.domain.subscription.SubscriptionRepository;
import io.forklore.domain.user.User;
import io.forklore.dto.response.SubscriptionResponse;
import io.forklore.global.error.EntityNotFoundException;
import io.forklore.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class SubscriptionService {

    private final SubscriptionRepository subscriptionRepository;
    private final UserRepository userRepository;

    /**
     * 구독 생성
     */
    @Transactional
    public SubscriptionResponse subscribe(Long userId, PlanType planType, boolean autoRenew) {
        User user = userRepository.findById(userId)
                .orElseThrow(EntityNotFoundException::new);

        // 이미 활성 구독이 있는지 확인
        if (hasActiveSubscription(userId)) {
            throw new IllegalStateException("이미 활성화된 구독이 있습니다.");
        }

        Subscription subscription = Subscription.builder()
                .user(user)
                .planType(planType)
                .startDate(LocalDate.now())
                .autoRenew(autoRenew)
                .build();

        Subscription saved = subscriptionRepository.save(subscription);
        return SubscriptionResponse.from(saved);
    }

    /**
     * 구독 취소 (다음 갱신 해지)
     */
    @Transactional
    public SubscriptionResponse cancel(Long userId) {
        Subscription subscription = getActiveSubscription(userId)
                .orElseThrow(() -> new IllegalStateException("활성화된 구독이 없습니다."));

        subscription.cancel();
        return SubscriptionResponse.from(subscription);
    }

    /**
     * 요금제 변경
     */
    @Transactional
    public SubscriptionResponse changePlan(Long userId, PlanType newPlanType) {
        Subscription subscription = getActiveSubscription(userId)
                .orElseThrow(() -> new IllegalStateException("활성화된 구독이 없습니다."));

        subscription.changePlan(newPlanType);
        return SubscriptionResponse.from(subscription);
    }

    /**
     * 현재 구독 상태 조회
     */
    public Optional<SubscriptionResponse> getStatus(Long userId) {
        return getActiveSubscription(userId)
                .map(SubscriptionResponse::from);
    }

    /**
     * 구독 내역 조회
     */
    public List<SubscriptionResponse> getHistory(Long userId) {
        return subscriptionRepository.findByUserIdOrderByCreatedAtDesc(userId)
                .stream()
                .map(SubscriptionResponse::from)
                .collect(Collectors.toList());
    }

    /**
     * 활성 구독 여부 확인
     */
    public boolean hasActiveSubscription(Long userId) {
        return subscriptionRepository.existsActiveByUserId(userId, LocalDate.now());
    }

    /**
     * 활성 구독 조회
     */
    public Optional<Subscription> getActiveSubscription(Long userId) {
        return subscriptionRepository.findActiveByUserId(userId);
    }

    /**
     * 만료된 구독 처리 (스케줄러에서 호출)
     */
    @Transactional
    public int expireSubscriptions() {
        List<Subscription> expiring = subscriptionRepository.findExpiringSoon(LocalDate.now());

        for (Subscription subscription : expiring) {
            if (subscription.isExpired()) {
                subscription.expire();
            }
        }

        return expiring.size();
    }

    /**
     * 자동 갱신 처리 (스케줄러에서 호출)
     */
    @Transactional
    public int renewSubscriptions() {
        List<Subscription> forRenewal = subscriptionRepository.findForRenewal(LocalDate.now());

        for (Subscription subscription : forRenewal) {
            // TODO: 결제 처리 로직 연동
            subscription.renew();
        }

        return forRenewal.size();
    }
}
