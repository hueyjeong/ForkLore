package io.forklore.domain.purchase;

import io.forklore.domain.chapter.Chapter;
import io.forklore.domain.user.User;
import io.forklore.global.common.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 회차 구매 엔티티
 * 개별 회차 구매(소장) 내역 관리
 */
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "purchases", uniqueConstraints = {
        @UniqueConstraint(columnNames = { "user_id", "chapter_id" })
})
public class Purchase extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "chapter_id", nullable = false)
    private Chapter chapter;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    @Column(name = "purchased_at", nullable = false)
    private LocalDateTime purchasedAt;

    @Builder
    public Purchase(User user, Chapter chapter, BigDecimal price) {
        this.user = user;
        this.chapter = chapter;
        this.price = price;
        this.purchasedAt = LocalDateTime.now();
    }
}
