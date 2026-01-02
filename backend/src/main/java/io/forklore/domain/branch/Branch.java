package io.forklore.domain.branch;

import io.forklore.domain.novel.Novel;
import io.forklore.domain.user.User;
import io.forklore.global.common.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.SQLRestriction;

/**
 * 브랜치 엔티티
 * - 메인 브랜치 (is_main=true): 원작 정사
 * - 파생 브랜치 (is_main=false): 외전/팬픽/IF
 */
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "branches")
@SQLRestriction("deleted_at IS NULL")
public class Branch extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "novel_id", nullable = false)
    private Novel novel;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private User author;

    @Column(name = "is_main", nullable = false)
    private boolean isMain;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_branch_id")
    private Branch parentBranch;

    @Column(name = "fork_point_chapter")
    private Integer forkPointChapter;

    @Column(nullable = false, length = 200)
    private String name;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(name = "cover_image_url", length = 500)
    private String coverImageUrl;

    @Enumerated(EnumType.STRING)
    @Column(name = "branch_type", nullable = false, length = 20)
    private BranchType branchType;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private BranchVisibility visibility;

    @Enumerated(EnumType.STRING)
    @Column(name = "canon_status", nullable = false, length = 20)
    private CanonStatus canonStatus;

    @Column(name = "merged_at_chapter")
    private Integer mergedAtChapter;

    @Column(name = "vote_count", nullable = false)
    private long voteCount;

    @Column(name = "vote_threshold", nullable = false)
    private int voteThreshold;

    @Column(name = "view_count", nullable = false)
    private long viewCount;

    @Column(name = "chapter_count", nullable = false)
    private int chapterCount;

    @Builder
    public Branch(Novel novel, User author, boolean isMain, Branch parentBranch, 
                  Integer forkPointChapter, String name, String description,
                  String coverImageUrl, BranchType branchType, BranchVisibility visibility) {
        this.novel = novel;
        this.author = author;
        this.isMain = isMain;
        this.parentBranch = parentBranch;
        this.forkPointChapter = forkPointChapter;
        this.name = name;
        this.description = description;
        this.coverImageUrl = coverImageUrl;
        this.branchType = branchType != null ? branchType : BranchType.FAN_FIC;
        this.visibility = visibility != null ? visibility : BranchVisibility.PRIVATE;
        this.canonStatus = CanonStatus.NON_CANON;
        this.voteCount = 0;
        this.voteThreshold = 1000;
        this.viewCount = 0;
        this.chapterCount = 0;
    }

    /**
     * 메인 브랜치 생성을 위한 정적 팩토리 메서드
     */
    public static Branch createMainBranch(Novel novel, User author) {
        return Branch.builder()
                .novel(novel)
                .author(author)
                .isMain(true)
                .name(novel.getTitle())
                .description(novel.getDescription())
                .branchType(BranchType.MAIN)
                .visibility(BranchVisibility.PUBLIC)
                .build();
    }

    /**
     * 브랜치 정보 수정
     */
    public void update(String name, String description, String coverImageUrl) {
        if (name != null) this.name = name;
        if (description != null) this.description = description;
        if (coverImageUrl != null) this.coverImageUrl = coverImageUrl;
    }

    /**
     * 가시성 변경
     */
    public void changeVisibility(BranchVisibility visibility) {
        this.visibility = visibility;
    }

    /**
     * 투표 수 증가
     */
    public void incrementVoteCount() {
        this.voteCount++;
    }

    /**
     * 투표 수 감소
     */
    public void decrementVoteCount() {
        if (this.voteCount > 0) {
            this.voteCount--;
        }
    }

    /**
     * 조회수 증가
     */
    public void incrementViewCount() {
        this.viewCount++;
    }

    /**
     * 회차 수 증가
     */
    public void incrementChapterCount() {
        this.chapterCount++;
    }

    /**
     * 정사 편입 후보 지정
     */
    public void markAsCandidate() {
        this.canonStatus = CanonStatus.CANDIDATE;
    }

    /**
     * 정사 편입
     */
    public void mergeToCanon(int atChapter) {
        this.canonStatus = CanonStatus.MERGED;
        this.mergedAtChapter = atChapter;
    }
}
