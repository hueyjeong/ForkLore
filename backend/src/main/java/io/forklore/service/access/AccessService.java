package io.forklore.service.access;

import io.forklore.domain.chapter.AccessType;
import io.forklore.domain.chapter.Chapter;
import io.forklore.domain.chapter.ChapterRepository;
import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.purchase.PurchaseRepository;
import io.forklore.domain.subscription.SubscriptionRepository;
import io.forklore.domain.user.User;
import io.forklore.global.error.EntityNotFoundException;
import io.forklore.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.Period;

/**
 * 회차 접근 권한 판단 서비스
 * 무료/유료/구독/연령제한 등 복합적인 접근 조건 판단
 */
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class AccessService {

    private final ChapterRepository chapterRepository;
    private final SubscriptionRepository subscriptionRepository;
    private final PurchaseRepository purchaseRepository;
    private final UserRepository userRepository;

    /**
     * 회차 접근 가능 여부 확인
     * 
     * @return true if user can access the chapter
     */
    public boolean canAccessChapter(Long userId, Long chapterId) {
        Chapter chapter = chapterRepository.findById(chapterId)
                .orElseThrow(EntityNotFoundException::new);

        // 1. 무료 회차면 바로 접근 가능
        if (chapter.getAccessType() == AccessType.FREE) {
            return true;
        }

        // 비로그인 사용자는 유료 콘텐츠 접근 불가
        if (userId == null) {
            return false;
        }

        // 2. 구매한 회차인지 확인
        if (purchaseRepository.existsByUserIdAndChapterId(userId, chapterId)) {
            return true;
        }

        // 3. 활성 구독이 있는지 확인
        if (subscriptionRepository.existsActiveByUserId(userId, LocalDate.now())) {
            return true;
        }

        return false;
    }

    /**
     * 연령 제한 확인
     * 
     * @return true if user meets age requirement
     */
    public boolean checkAgeRating(Long userId, Long novelId) {
        if (userId == null) {
            return false;
        }

        User user = userRepository.findById(userId)
                .orElseThrow(EntityNotFoundException::new);

        // 사용자 생년월일이 없으면 제한된 콘텐츠 접근 불가
        if (user.getBirthDate() == null) {
            return false;
        }

        Novel novel = chapterRepository.findById(novelId)
                .map(Chapter::getBranch)
                .map(branch -> branch.getNovel())
                .orElseThrow(EntityNotFoundException::new);

        int userAge = calculateAge(user.getBirthDate());
        AgeRating ageRating = novel.getAgeRating();

        return switch (ageRating) {
            case ALL -> true;
            case R12 -> userAge >= 12;
            case R15 -> userAge >= 15;
            case R19 -> userAge >= 19;
        };
    }

    /**
     * 접근 결과 상세 (왜 접근 불가인지 포함)
     */
    public AccessResult checkAccess(Long userId, Long chapterId) {
        Chapter chapter = chapterRepository.findById(chapterId)
                .orElseThrow(EntityNotFoundException::new);

        // 무료 회차
        if (chapter.getAccessType() == AccessType.FREE) {
            return AccessResult.allowed();
        }

        // 비로그인
        if (userId == null) {
            return AccessResult.denied("로그인이 필요합니다.");
        }

        // 구매 확인
        if (purchaseRepository.existsByUserIdAndChapterId(userId, chapterId)) {
            return AccessResult.allowed();
        }

        // 구독 확인
        if (subscriptionRepository.existsActiveByUserId(userId, LocalDate.now())) {
            return AccessResult.allowed();
        }

        return AccessResult.denied("구독 또는 개별 구매가 필요합니다.", chapter.getPrice());
    }

    private int calculateAge(LocalDate birthDate) {
        return Period.between(birthDate, LocalDate.now()).getYears();
    }

    /**
     * 접근 결과 DTO
     */
    public record AccessResult(
            boolean allowed,
            String reason,
            Integer requiredPrice) {
        public static AccessResult allowed() {
            return new AccessResult(true, null, null);
        }

        public static AccessResult denied(String reason) {
            return new AccessResult(false, reason, null);
        }

        public static AccessResult denied(String reason, int price) {
            return new AccessResult(false, reason, price);
        }
    }
}
