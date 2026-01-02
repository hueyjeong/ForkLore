package io.forklore.domain.subscription;

import io.forklore.domain.user.User;
import io.forklore.global.common.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

/**
 * 구독 엔티티
 * 사용자의 구독 정보 관리
 */
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "subscriptions")
public class Subscription extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Enumerated(EnumType.STRING)
    @Column(name = "plan_type", nullable = false, length = 20)
    private PlanType planType;

    @Column(name = "start_date", nullable = false)
    private LocalDate startDate;

    @Column(name = "end_date", nullable = false)
    private LocalDate endDate;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private SubscriptionStatus status;

    @Column(name = "auto_renew", nullable = false)
    private boolean autoRenew;

    @Builder
    public Subscription(User user, PlanType planType, LocalDate startDate, boolean autoRenew) {
        this.user = user;
        this.planType = planType;
        this.startDate = startDate != null ? startDate : LocalDate.now();
        this.endDate = this.startDate.plusDays(planType.getDurationDays());
        this.status = SubscriptionStatus.ACTIVE;
        this.autoRenew = autoRenew;
    }

    /**
     * 구독 취소 (다음 갱신 해지)
     */
    public void cancel() {
        this.autoRenew = false;
        this.status = SubscriptionStatus.CANCELLED;
    }

    /**
     * 구독 갱신
     */
    public void renew() {
        this.startDate = this.endDate;
        this.endDate = this.startDate.plusDays(planType.getDurationDays());
        this.status = SubscriptionStatus.ACTIVE;
    }

    /**
     * 요금제 변경
     */
    public void changePlan(PlanType newPlanType) {
        this.planType = newPlanType;
        this.endDate = this.startDate.plusDays(newPlanType.getDurationDays());
    }

    /**
     * 구독 만료 처리
     */
    public void expire() {
        this.status = SubscriptionStatus.EXPIRED;
    }

    /**
     * 현재 활성 상태인지 확인
     */
    public boolean isActive() {
        return this.status == SubscriptionStatus.ACTIVE &&
                !LocalDate.now().isAfter(this.endDate);
    }

    /**
     * 만료 여부 확인
     */
    public boolean isExpired() {
        return LocalDate.now().isAfter(this.endDate);
    }

    /**
     * 남은 일수 계산
     */
    public long getRemainingDays() {
        if (isExpired()) {
            return 0;
        }
        return java.time.temporal.ChronoUnit.DAYS.between(LocalDate.now(), this.endDate);
    }
}
