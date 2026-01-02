package io.forklore.domain.subscription;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

public interface SubscriptionRepository extends JpaRepository<Subscription, Long> {

    /**
     * 사용자의 활성 구독 조회
     */
    @Query("SELECT s FROM Subscription s WHERE s.user.id = :userId AND s.status = 'ACTIVE' AND s.endDate >= :now")
    Optional<Subscription> findActiveByUserId(@Param("userId") Long userId, @Param("now") LocalDate now);

    /**
     * 사용자의 현재 활성 구독 조회 (현재 날짜 기준)
     */
    default Optional<Subscription> findActiveByUserId(Long userId) {
        return findActiveByUserId(userId, LocalDate.now());
    }

    /**
     * 사용자의 모든 구독 내역 조회
     */
    List<Subscription> findByUserIdOrderByCreatedAtDesc(Long userId);

    /**
     * 사용자 + 상태로 조회
     */
    List<Subscription> findByUserIdAndStatus(Long userId, SubscriptionStatus status);

    /**
     * 활성 구독 존재 여부 확인
     */
    @Query("SELECT COUNT(s) > 0 FROM Subscription s WHERE s.user.id = :userId AND s.status = 'ACTIVE' AND s.endDate >= :now")
    boolean existsActiveByUserId(@Param("userId") Long userId, @Param("now") LocalDate now);

    /**
     * 만료 예정 구독 조회 (스케줄러용)
     */
    @Query("SELECT s FROM Subscription s WHERE s.status = 'ACTIVE' AND s.endDate <= :date")
    List<Subscription> findExpiringSoon(@Param("date") LocalDate date);

    /**
     * 갱신 대상 구독 조회 (스케줄러용)
     */
    @Query("SELECT s FROM Subscription s WHERE s.status = 'ACTIVE' AND s.autoRenew = true AND s.endDate = :date")
    List<Subscription> findForRenewal(@Param("date") LocalDate date);
}
