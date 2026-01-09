package io.forklore.dto.response;

import io.forklore.domain.purchase.Purchase;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "구매 내역 응답")
public class PurchaseResponse {

    @Schema(description = "구매 ID")
    private Long id;

    @Schema(description = "회차 ID")
    private Long chapterId;

    @Schema(description = "회차 제목")
    private String chapterTitle;

    @Schema(description = "회차 번호")
    private int chapterNumber;

    @Schema(description = "구매 가격")
    private BigDecimal price;

    @Schema(description = "구매 일시")
    private LocalDateTime purchasedAt;

    public static PurchaseResponse from(Purchase purchase) {
        return PurchaseResponse.builder()
                .id(purchase.getId())
                .chapterId(purchase.getChapter().getId())
                .chapterTitle(purchase.getChapter().getTitle())
                .chapterNumber(purchase.getChapter().getChapterNumber())
                .price(purchase.getPrice())
                .purchasedAt(purchase.getPurchasedAt())
                .build();
    }
}
