package io.forklore.domain.purchase;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface PurchaseRepository extends JpaRepository<Purchase, Long> {

    /**
     * 구매 여부 확인
     */
    boolean existsByUserIdAndChapterId(Long userId, Long chapterId);

    /**
     * 사용자+회차로 구매 내역 조회
     */
    Optional<Purchase> findByUserIdAndChapterId(Long userId, Long chapterId);

    /**
     * 사용자의 구매 목록 조회
     */
    List<Purchase> findByUserIdOrderByPurchasedAtDesc(Long userId);

    /**
     * 사용자의 구매 목록 조회 (페이징)
     */
    Page<Purchase> findByUserId(Long userId, Pageable pageable);

    /**
     * 특정 회차 구매 수
     */
    int countByChapterId(Long chapterId);
}
