package io.forklore.domain.branch;

import io.forklore.domain.user.User;
import io.forklore.global.common.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 브랜치 연결 요청 엔티티
 * 팬 창작물을 원작 소설 페이지에 연결 요청
 */
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "branch_link_requests")
public class BranchLinkRequest extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "branch_id", nullable = false)
    private Branch branch;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private LinkRequestStatus status;

    @Column(name = "request_message", columnDefinition = "TEXT")
    private String requestMessage;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "reviewer_id")
    private User reviewer;

    @Column(name = "review_comment", columnDefinition = "TEXT")
    private String reviewComment;

    @Column(name = "reviewed_at")
    private LocalDateTime reviewedAt;

    @Builder
    public BranchLinkRequest(Branch branch, String requestMessage) {
        this.branch = branch;
        this.requestMessage = requestMessage;
        this.status = LinkRequestStatus.PENDING;
    }

    /**
     * 연결 요청 승인
     */
    public void approve(User reviewer, String comment) {
        this.status = LinkRequestStatus.APPROVED;
        this.reviewer = reviewer;
        this.reviewComment = comment;
        this.reviewedAt = LocalDateTime.now();
        
        // 브랜치 가시성을 LINKED로 변경
        this.branch.changeVisibility(BranchVisibility.LINKED);
    }

    /**
     * 연결 요청 거절
     */
    public void reject(User reviewer, String comment) {
        this.status = LinkRequestStatus.REJECTED;
        this.reviewer = reviewer;
        this.reviewComment = comment;
        this.reviewedAt = LocalDateTime.now();
    }

    /**
     * 대기 중인 요청인지 확인
     */
    public boolean isPending() {
        return this.status == LinkRequestStatus.PENDING;
    }
}
