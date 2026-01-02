package io.forklore.domain.novel;

import io.forklore.global.common.BaseEntity;
import io.forklore.domain.user.User;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import org.hibernate.annotations.SQLRestriction;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "novels")
@SQLRestriction("deleted_at IS NULL")
public class Novel extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private User author;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(length = 500)
    private String coverImageUrl;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 50)
    private Genre genre;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 10)
    private AgeRating ageRating;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private NovelStatus status;

    @Column(nullable = false)
    private boolean allowBranching;

    @Column(nullable = false)
    private long totalViewCount;

    @Column(nullable = false)
    private long totalLikeCount;

    @Column(nullable = false)
    private int totalChapterCount;

    @Column(nullable = false)
    private int branchCount;

    @Builder
    public Novel(User author, String title, String description, String coverImageUrl, Genre genre, AgeRating ageRating, Boolean allowBranching) {
        this.author = author;
        this.title = title;
        this.description = description;
        this.coverImageUrl = coverImageUrl;
        this.genre = genre;
        this.ageRating = ageRating != null ? ageRating : AgeRating.ALL;
        this.status = NovelStatus.ONGOING;
        this.allowBranching = allowBranching != null ? allowBranching : true;
        this.totalViewCount = 0;
        this.totalLikeCount = 0;
        this.totalChapterCount = 0;
        this.branchCount = 1; // Default 1 for main branch
    }

    public void update(String title, String description, String coverImageUrl, Genre genre, AgeRating ageRating, NovelStatus status, Boolean allowBranching) {
        if (title != null) this.title = title;
        if (description != null) this.description = description;
        if (coverImageUrl != null) this.coverImageUrl = coverImageUrl;
        if (genre != null) this.genre = genre;
        if (ageRating != null) this.ageRating = ageRating;
        if (status != null) this.status = status;
        if (allowBranching != null) this.allowBranching = allowBranching;
    }
}
