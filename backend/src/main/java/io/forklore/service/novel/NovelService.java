package io.forklore.service.novel;

import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.novel.NovelRepository;
import io.forklore.domain.novel.NovelStatus;
import io.forklore.domain.user.User;
import io.forklore.dto.request.NovelCreateRequest;
import io.forklore.dto.request.NovelUpdateRequest;
import io.forklore.dto.response.NovelResponse;
import io.forklore.dto.response.NovelSummaryResponse;
import io.forklore.global.error.EntityNotFoundException;
import io.forklore.global.error.UnauthorizedException;
import io.forklore.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class NovelService {

    private final NovelRepository novelRepository;
    private final UserRepository userRepository;

    /**
     * 소설 생성
     * TODO: 메인 브랜치 자동 생성 로직 연동 (Branch 엔티티 구현 후)
     */
    @Transactional
    public NovelResponse create(Long userId, NovelCreateRequest request) {
        User author = userRepository.findById(userId)
                .orElseThrow(EntityNotFoundException::new);

        Novel novel = Novel.builder()
                .author(author)
                .title(request.getTitle())
                .description(request.getDescription())
                .coverImageUrl(request.getCoverImageUrl())
                .genre(request.getGenre())
                .ageRating(request.getAgeRating())
                .allowBranching(request.getAllowBranching())
                .build();

        Novel saved = novelRepository.save(novel);
        
        // TODO: BranchService.createMainBranch(novel) 호출
        
        return NovelResponse.from(saved);
    }

    /**
     * 소설 목록 조회 (필터링, 페이징)
     */
    public Page<NovelSummaryResponse> getList(Genre genre, NovelStatus status, Pageable pageable) {
        Page<Novel> novels;
        
        if (genre != null && status != null) {
            novels = novelRepository.findByGenreAndStatus(genre, status, pageable);
        } else if (genre != null) {
            novels = novelRepository.findByGenre(genre, pageable);
        } else if (status != null) {
            novels = novelRepository.findByStatus(status, pageable);
        } else {
            novels = novelRepository.findAll(pageable);
        }
        
        return novels.map(NovelSummaryResponse::from);
    }

    /**
     * 소설 상세 조회
     */
    public NovelResponse getDetail(Long novelId) {
        Novel novel = novelRepository.findById(novelId)
                .orElseThrow(EntityNotFoundException::new);
        return NovelResponse.from(novel);
    }

    /**
     * 소설 수정 (작가 본인만)
     */
    @Transactional
    public NovelResponse update(Long userId, Long novelId, NovelUpdateRequest request) {
        Novel novel = novelRepository.findById(novelId)
                .orElseThrow(EntityNotFoundException::new);

        if (!novel.getAuthor().getId().equals(userId)) {
            throw new UnauthorizedException();
        }

        novel.update(
                request.getTitle(),
                request.getDescription(),
                request.getCoverImageUrl(),
                request.getGenre(),
                request.getAgeRating(),
                request.getStatus(),
                request.getAllowBranching()
        );

        return NovelResponse.from(novel);
    }

    /**
     * 소설 삭제 (소프트 삭제, 작가 본인만)
     */
    @Transactional
    public void delete(Long userId, Long novelId) {
        Novel novel = novelRepository.findById(novelId)
                .orElseThrow(EntityNotFoundException::new);

        if (!novel.getAuthor().getId().equals(userId)) {
            throw new UnauthorizedException();
        }

        novel.setDeletedAt(LocalDateTime.now());
    }
}
