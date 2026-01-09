package io.forklore.domain.chapter;

import io.forklore.domain.branch.Branch;
import io.forklore.global.common.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 회차 엔티티
 * 스토리의 기본 단위
 */
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "chapters", uniqueConstraints = {
        @UniqueConstraint(columnNames = { "branch_id", "chapter_number" })
})
public class Chapter extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "branch_id", nullable = false)
    private Branch branch;

    @Column(name = "chapter_number", nullable = false)
    private int chapterNumber;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String content;

    @Column(name = "content_html", columnDefinition = "TEXT")
    private String contentHtml;

    @Column(name = "word_count", nullable = false)
    private int wordCount;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private ChapterStatus status;

    @Enumerated(EnumType.STRING)
    @Column(name = "access_type", nullable = false, length = 20)
    private AccessType accessType;

    @Column(nullable = false)
    private int price;

    @Column(name = "author_comment", columnDefinition = "TEXT")
    private String authorComment;

    @Column(name = "scheduled_at")
    private LocalDateTime scheduledAt;

    @Column(name = "published_at")
    private LocalDateTime publishedAt;

    @Column(name = "view_count", nullable = false)
    private long viewCount;

    @Column(name = "like_count", nullable = false)
    private long likeCount;

    @Column(name = "comment_count", nullable = false)
    private int commentCount;

    @Builder
    public Chapter(Branch branch, int chapterNumber, String title, String content,
            String contentHtml, int wordCount, AccessType accessType, int price,
            String authorComment) {
        this.branch = branch;
        this.chapterNumber = chapterNumber;
        this.title = title;
        this.content = content;
        this.contentHtml = contentHtml;
        this.wordCount = wordCount;
        this.status = ChapterStatus.DRAFT;
        this.accessType = accessType != null ? accessType : AccessType.FREE;
        this.price = price;
        this.authorComment = authorComment;
        this.viewCount = 0;
        this.likeCount = 0;
        this.commentCount = 0;
    }

    /**
     * 회차 내용 수정
     */
    public void update(String title, String content, String contentHtml, int wordCount,
            AccessType accessType, Integer price, String authorComment) {
        if (title != null)
            this.title = title;
        if (content != null) {
            this.content = content;
            this.contentHtml = contentHtml;
            this.wordCount = wordCount;
        }
        if (accessType != null)
            this.accessType = accessType;
        if (price != null)
            this.price = price;
        if (authorComment != null)
            this.authorComment = authorComment;
    }

    /**
     * 발행
     */
    public void publish() {
        this.status = ChapterStatus.PUBLISHED;
        this.publishedAt = LocalDateTime.now();
        this.scheduledAt = null;
    }

    /**
     * 예약 발행 설정
     */
    public void schedule(LocalDateTime scheduledAt) {
        this.status = ChapterStatus.SCHEDULED;
        this.scheduledAt = scheduledAt;
    }

    /**
     * 예약 시간 도래 시 자동 발행
     */
    public void autoPublish() {
        if (this.status == ChapterStatus.SCHEDULED &&
                this.scheduledAt != null &&
                LocalDateTime.now().isAfter(this.scheduledAt)) {
            publish();
        }
    }

    /**
     * 조회수 증가
     */
    public void incrementViewCount() {
        this.viewCount++;
    }

    /**
     * 좋아요 수 증가
     */
    public void incrementLikeCount() {
        this.likeCount++;
    }

    /**
     * 좋아요 수 감소
     */
    public void decrementLikeCount() {
        if (this.likeCount > 0) {
            this.likeCount--;
        }
    }

    /**
     * 댓글 수 증가
     */
    public void incrementCommentCount() {
        this.commentCount++;
    }

    /**
     * 댓글 수 감소
     */
    public void decrementCommentCount() {
        if (this.commentCount > 0) {
            this.commentCount--;
        }
    }

    /**
     * 발행된 상태인지 확인
     */
    public boolean isPublished() {
        return this.status == ChapterStatus.PUBLISHED;
    }
}
