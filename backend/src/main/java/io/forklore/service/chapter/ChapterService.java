package io.forklore.service.chapter;

import io.forklore.domain.branch.Branch;
import io.forklore.domain.branch.BranchRepository;
import io.forklore.domain.chapter.Chapter;
import io.forklore.domain.chapter.ChapterRepository;
import io.forklore.domain.chapter.ChapterStatus;
import io.forklore.dto.request.ChapterCreateRequest;
import io.forklore.dto.request.ChapterUpdateRequest;
import io.forklore.dto.response.ChapterResponse;
import io.forklore.dto.response.ChapterSummaryResponse;
import io.forklore.global.error.EntityNotFoundException;
import io.forklore.global.error.UnauthorizedException;
import io.forklore.util.MarkdownParser;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class ChapterService {

    private final ChapterRepository chapterRepository;
    private final BranchRepository branchRepository;
    private final MarkdownParser markdownParser;

    /**
     * 회차 생성 (초안)
     */
    @Transactional
    public ChapterResponse create(Long branchId, Long userId, ChapterCreateRequest request) {
        Branch branch = branchRepository.findById(branchId)
                .orElseThrow(EntityNotFoundException::new);

        // 브랜치 작가인지 확인
        validateBranchOwnership(branch, userId);

        // 다음 회차 번호 결정
        int nextChapterNumber = chapterRepository.findTopByBranchIdOrderByChapterNumberDesc(branchId)
                .map(c -> c.getChapterNumber() + 1)
                .orElse(1);

        // 마크다운 → HTML 변환
        String contentHtml = markdownParser.toHtml(request.getContent());
        int wordCount = markdownParser.countWords(request.getContent());

        Chapter chapter = Chapter.builder()
                .branch(branch)
                .chapterNumber(nextChapterNumber)
                .title(request.getTitle())
                .content(request.getContent())
                .contentHtml(contentHtml)
                .wordCount(wordCount)
                .accessType(request.getAccessType())
                .price(request.getPrice() != null ? request.getPrice() : 0)
                .authorComment(request.getAuthorComment())
                .build();

        Chapter saved = chapterRepository.save(chapter);

        // 브랜치의 회차 수 증가
        branch.incrementChapterCount();

        return ChapterResponse.from(saved);
    }

    /**
     * 회차 수정
     */
    @Transactional
    public ChapterResponse update(Long chapterId, Long userId, ChapterUpdateRequest request) {
        Chapter chapter = chapterRepository.findById(chapterId)
                .orElseThrow(EntityNotFoundException::new);

        validateBranchOwnership(chapter.getBranch(), userId);

        // 마크다운 변환 (content가 변경된 경우에만)
        String contentHtml = null;
        int wordCount = chapter.getWordCount();
        if (request.getContent() != null) {
            contentHtml = markdownParser.toHtml(request.getContent());
            wordCount = markdownParser.countWords(request.getContent());
        }

        chapter.update(
                request.getTitle(),
                request.getContent(),
                contentHtml,
                wordCount,
                request.getAccessType(),
                request.getPrice(),
                request.getAuthorComment());

        return ChapterResponse.from(chapter);
    }

    /**
     * 회차 발행
     */
    @Transactional
    public ChapterResponse publish(Long chapterId, Long userId) {
        Chapter chapter = chapterRepository.findById(chapterId)
                .orElseThrow(EntityNotFoundException::new);

        validateBranchOwnership(chapter.getBranch(), userId);

        chapter.publish();

        return ChapterResponse.from(chapter);
    }

    /**
     * 회차 예약 발행
     */
    @Transactional
    public ChapterResponse schedule(Long chapterId, Long userId, LocalDateTime scheduledAt) {
        Chapter chapter = chapterRepository.findById(chapterId)
                .orElseThrow(EntityNotFoundException::new);

        validateBranchOwnership(chapter.getBranch(), userId);

        if (scheduledAt.isBefore(LocalDateTime.now())) {
            throw new IllegalArgumentException("예약 시간은 현재 시간 이후여야 합니다.");
        }

        chapter.schedule(scheduledAt);

        return ChapterResponse.from(chapter);
    }

    /**
     * 브랜치의 회차 목록 조회 (목차)
     */
    public List<ChapterSummaryResponse> getList(Long branchId, boolean publishedOnly) {
        List<Chapter> chapters;

        if (publishedOnly) {
            chapters = chapterRepository.findByBranchIdAndStatusOrderByChapterNumberAsc(
                    branchId, ChapterStatus.PUBLISHED);
        } else {
            chapters = chapterRepository.findByBranchIdOrderByChapterNumberAsc(branchId);
        }

        return chapters.stream()
                .map(ChapterSummaryResponse::from)
                .collect(Collectors.toList());
    }

    /**
     * 회차 상세 조회
     */
    public ChapterResponse getDetail(Long chapterId) {
        Chapter chapter = chapterRepository.findById(chapterId)
                .orElseThrow(EntityNotFoundException::new);

        return ChapterResponse.from(chapter);
    }

    /**
     * 회차 상세 조회 + 조회수 증가
     */
    @Transactional
    public ChapterResponse getDetailWithViewCount(Long chapterId) {
        Chapter chapter = chapterRepository.findById(chapterId)
                .orElseThrow(EntityNotFoundException::new);

        chapter.incrementViewCount();

        return ChapterResponse.from(chapter);
    }

    /**
     * 예약된 회차 자동 발행 (스케줄러에서 호출)
     */
    @Transactional
    public int publishScheduledChapters() {
        List<Chapter> scheduledChapters = chapterRepository.findScheduledForPublish(LocalDateTime.now());

        for (Chapter chapter : scheduledChapters) {
            chapter.publish();
        }

        return scheduledChapters.size();
    }

    private void validateBranchOwnership(Branch branch, Long userId) {
        if (!branch.getAuthor().getId().equals(userId)) {
            throw new UnauthorizedException();
        }
    }
}
