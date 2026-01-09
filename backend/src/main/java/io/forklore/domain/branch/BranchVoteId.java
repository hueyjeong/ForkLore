package io.forklore.domain.branch;

import java.io.Serializable;
import java.util.Objects;

/**
 * BranchVote 복합 키 클래스
 */
public class BranchVoteId implements Serializable {

    private Long userId;
    private Long branchId;

    public BranchVoteId() {
    }

    public BranchVoteId(Long userId, Long branchId) {
        this.userId = userId;
        this.branchId = branchId;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        BranchVoteId that = (BranchVoteId) o;
        return Objects.equals(userId, that.userId) && Objects.equals(branchId, that.branchId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(userId, branchId);
    }
}
