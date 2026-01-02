package io.forklore.domain.branch;

import org.springframework.data.jpa.repository.JpaRepository;

public interface BranchVoteRepository extends JpaRepository<BranchVote, BranchVoteId> {

    /**
     * 사용자가 특정 브랜치에 투표했는지 확인
     */
    boolean existsByUserIdAndBranchId(Long userId, Long branchId);

    /**
     * 사용자의 특정 브랜치 투표 삭제
     */
    void deleteByUserIdAndBranchId(Long userId, Long branchId);

    /**
     * 특정 브랜치의 투표 수 조회
     */
    long countByBranchId(Long branchId);
}
