package io.forklore.domain.branch;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface BranchLinkRequestRepository extends JpaRepository<BranchLinkRequest, Long> {

    /**
     * 특정 브랜치의 연결 요청 목록 조회
     */
    List<BranchLinkRequest> findByBranchId(Long branchId);

    /**
     * 상태별 연결 요청 조회
     */
    Page<BranchLinkRequest> findByStatus(LinkRequestStatus status, Pageable pageable);

    /**
     * 특정 브랜치의 대기 중인 요청이 있는지 확인
     */
    boolean existsByBranchIdAndStatus(Long branchId, LinkRequestStatus status);
}
