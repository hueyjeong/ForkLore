package io.forklore.security.aop;

import io.forklore.domain.chapter.AccessType;
import io.forklore.domain.chapter.Chapter;
import io.forklore.domain.chapter.ChapterRepository;
import io.forklore.global.error.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

/**
 * 회차 접근 권한 검사기
 * 
 * AccessService 호환 인터페이스. PR #99, #100, #101 병합 후
 * AccessService로 교체하거나 위임할 수 있습니다.
 */
@Component
@RequiredArgsConstructor
public class AccessChecker {

    private final ChapterRepository chapterRepository;
    // AccessService, SubscriptionRepository, PurchaseRepository는
    // PR 병합 후 주입하여 사용

    /**
     * 회차 접근 권한 확인
     * 
     * 현재는 무료 회차만 접근 가능하도록 구현.
     * TODO: PR #99, #100, #101 병합 후 AccessService로 위임
     */
    public boolean canAccessChapter(Long userId, Long chapterId) {
        Chapter chapter = chapterRepository.findById(chapterId)
                .orElseThrow(EntityNotFoundException::new);

        // 무료 회차는 누구나 접근 가능
        if (chapter.getAccessType() == AccessType.FREE) {
            return true;
        }

        // 유료 회차는 로그인 필요
        if (userId == null) {
            return false;
        }

        // TODO: 아래 로직은 PR 병합 후 활성화
        // 1. 구매 확인 - purchaseRepository.existsByUserIdAndChapterId(userId, chapterId)
        // 2. 구독 확인 - subscriptionRepository.existsActiveByUserId(userId,
        // LocalDate.now())

        // 현재는 인증된 사용자만 접근 가능 (임시)
        return true;
    }
}
