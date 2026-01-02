package io.forklore.domain.chapter;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public interface ChapterRepository extends JpaRepository<Chapter, Long> {

    /**
     * 브랜치의 전체 회차 목록 (번호 순 정렬)
     */
    List<Chapter> findByBranchIdOrderByChapterNumberAsc(Long branchId);

    /**
     * 브랜치의 발행된 회차 목록
     */
    List<Chapter> findByBranchIdAndStatusOrderByChapterNumberAsc(Long branchId, ChapterStatus status);

    /**
     * 브랜치의 회차 목록 (페이징)
     */
    Page<Chapter> findByBranchIdAndStatus(Long branchId, ChapterStatus status, Pageable pageable);

    /**
     * 예약 발행 대상 조회 (예약 시간 도래)
     */
    @Query("SELECT c FROM Chapter c WHERE c.status = 'SCHEDULED' AND c.scheduledAt <= :now")
    List<Chapter> findScheduledForPublish(@Param("now") LocalDateTime now);

    /**
     * 브랜치의 마지막 회차 번호 조회
     */
    Optional<Chapter> findTopByBranchIdOrderByChapterNumberDesc(Long branchId);

    /**
     * 특정 회차 번호로 조회
     */
    Optional<Chapter> findByBranchIdAndChapterNumber(Long branchId, int chapterNumber);

    /**
     * 브랜치의 회차 수 조회
     */
    int countByBranchId(Long branchId);

    /**
     * 브랜치의 발행된 회차 수 조회
     */
    int countByBranchIdAndStatus(Long branchId, ChapterStatus status);
}
