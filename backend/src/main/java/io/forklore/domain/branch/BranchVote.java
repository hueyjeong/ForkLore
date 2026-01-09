package io.forklore.domain.branch;

import io.forklore.domain.user.User;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 브랜치 투표 엔티티
 * 사용자가 브랜치에 투표 (중복 투표 방지)
 */
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "branch_votes")
@IdClass(BranchVoteId.class)
public class BranchVote {

    @Id
    @Column(name = "user_id")
    private Long userId;

    @Id
    @Column(name = "branch_id")
    private Long branchId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", insertable = false, updatable = false)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "branch_id", insertable = false, updatable = false)
    private Branch branch;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    public BranchVote(Long userId, Long branchId) {
        this.userId = userId;
        this.branchId = branchId;
        this.createdAt = LocalDateTime.now();
    }

    public static BranchVote create(User user, Branch branch) {
        return new BranchVote(user.getId(), branch.getId());
    }
}
