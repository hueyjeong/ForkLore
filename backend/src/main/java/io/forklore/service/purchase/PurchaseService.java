package io.forklore.service.purchase;

import io.forklore.domain.chapter.Chapter;
import io.forklore.domain.chapter.ChapterRepository;
import io.forklore.domain.purchase.Purchase;
import io.forklore.domain.purchase.PurchaseRepository;
import io.forklore.domain.user.User;
import io.forklore.dto.response.PurchaseResponse;
import io.forklore.global.error.EntityNotFoundException;
import io.forklore.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PurchaseService {

    private final PurchaseRepository purchaseRepository;
    private final ChapterRepository chapterRepository;
    private final UserRepository userRepository;

    /**
     * 회차 구매
     */
    @Transactional
    public PurchaseResponse purchase(Long userId, Long chapterId) {
        User user = userRepository.findById(userId)
                .orElseThrow(EntityNotFoundException::new);

        Chapter chapter = chapterRepository.findById(chapterId)
                .orElseThrow(EntityNotFoundException::new);

        // 이미 구매한 경우 예외
        if (hasPurchased(userId, chapterId)) {
            throw new IllegalStateException("이미 구매한 회차입니다.");
        }

        // TODO: 잔액 확인 및 차감 로직 (결제 모듈 연동)

        Purchase purchase = Purchase.builder()
                .user(user)
                .chapter(chapter)
                .price(BigDecimal.valueOf(chapter.getPrice()))
                .build();

        Purchase saved = purchaseRepository.save(purchase);
        return PurchaseResponse.from(saved);
    }

    /**
     * 구매 여부 확인
     */
    public boolean hasPurchased(Long userId, Long chapterId) {
        return purchaseRepository.existsByUserIdAndChapterId(userId, chapterId);
    }

    /**
     * 구매 목록 조회
     */
    public List<PurchaseResponse> getPurchaseList(Long userId) {
        return purchaseRepository.findByUserIdOrderByPurchasedAtDesc(userId)
                .stream()
                .map(PurchaseResponse::from)
                .collect(Collectors.toList());
    }
}
