package io.forklore.service.branch;

import io.forklore.domain.branch.*;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.novel.NovelRepository;
import io.forklore.domain.user.User;
import io.forklore.dto.request.BranchCreateRequest;
import io.forklore.dto.request.BranchUpdateRequest;
import io.forklore.dto.response.BranchResponse;
import io.forklore.dto.response.BranchSummaryResponse;
import io.forklore.global.error.EntityNotFoundException;
import io.forklore.global.error.UnauthorizedException;
import io.forklore.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class BranchService {

    private final BranchRepository branchRepository;
    private final BranchVoteRepository branchVoteRepository;
    private final NovelRepository novelRepository;
    private final UserRepository userRepository;

    /**
     * 메인 브랜치 생성 (소설 생성 시 자동 호출)
     */
    @Transactional
    public Branch createMainBranch(Novel novel, User author) {
        Branch mainBranch = Branch.createMainBranch(novel, author);
        return branchRepository.save(mainBranch);
    }

    /**
     * 브랜치 포크 (파생 브랜치 생성)
     */
    @Transactional
    public BranchResponse fork(Long novelId, Long userId, BranchCreateRequest request) {
        Novel novel = novelRepository.findById(novelId)
                .orElseThrow(EntityNotFoundException::new);

        // 브랜칭 허용 여부 확인
        if (!novel.isAllowBranching()) {
            throw new IllegalStateException("이 소설은 브랜치 작성이 허용되지 않습니다.");
        }

        User author = userRepository.findById(userId)
                .orElseThrow(EntityNotFoundException::new);

        Branch parentBranch = null;
        if (request.getParentBranchId() != null) {
            parentBranch = branchRepository.findById(request.getParentBranchId())
                    .orElseThrow(EntityNotFoundException::new);
        }

        Branch branch = Branch.builder()
                .novel(novel)
                .author(author)
                .isMain(false)
                .parentBranch(parentBranch)
                .forkPointChapter(request.getForkPointChapter())
                .name(request.getName())
                .description(request.getDescription())
                .coverImageUrl(request.getCoverImageUrl())
                .branchType(request.getBranchType())
                .visibility(request.getVisibility())
                .build();

        Branch saved = branchRepository.save(branch);
        
        // 소설의 브랜치 카운트 증가
        novel.update(null, null, null, null, null, null, null);

        return BranchResponse.from(saved);
    }

    /**
     * 소설의 공개 브랜치 목록 조회
     */
    public Page<BranchSummaryResponse> getPublicBranchList(Long novelId, Pageable pageable) {
        Page<Branch> branches = branchRepository.findByNovelIdAndVisibilityIn(
                novelId,
                List.of(BranchVisibility.PUBLIC, BranchVisibility.LINKED),
                pageable
        );
        return branches.map(BranchSummaryResponse::from);
    }

    /**
     * 브랜치 상세 조회
     */
    public BranchResponse getDetail(Long branchId) {
        Branch branch = branchRepository.findById(branchId)
                .orElseThrow(EntityNotFoundException::new);
        return BranchResponse.from(branch);
    }

    /**
     * 브랜치 수정 (작가 본인만)
     */
    @Transactional
    public BranchResponse update(Long userId, Long branchId, BranchUpdateRequest request) {
        Branch branch = branchRepository.findById(branchId)
                .orElseThrow(EntityNotFoundException::new);

        validateOwnership(branch, userId);

        branch.update(request.getName(), request.getDescription(), request.getCoverImageUrl());

        return BranchResponse.from(branch);
    }

    /**
     * 브랜치 삭제 (소프트 삭제, 작가 본인만)
     */
    @Transactional
    public void delete(Long userId, Long branchId) {
        Branch branch = branchRepository.findById(branchId)
                .orElseThrow(EntityNotFoundException::new);

        validateOwnership(branch, userId);

        // 메인 브랜치는 삭제 불가
        if (branch.isMain()) {
            throw new IllegalStateException("메인 브랜치는 삭제할 수 없습니다.");
        }

        branch.setDeletedAt(LocalDateTime.now());
    }

    /**
     * 가시성 변경 (작가 본인만)
     */
    @Transactional
    public BranchResponse changeVisibility(Long userId, Long branchId, BranchVisibility visibility) {
        Branch branch = branchRepository.findById(branchId)
                .orElseThrow(EntityNotFoundException::new);

        validateOwnership(branch, userId);

        // LINKED로 직접 변경 불가 (연결 요청 승인을 통해서만)
        if (visibility == BranchVisibility.LINKED) {
            throw new IllegalStateException("LINKED 상태는 연결 요청 승인을 통해서만 설정할 수 있습니다.");
        }

        branch.changeVisibility(visibility);

        return BranchResponse.from(branch);
    }

    /**
     * 브랜치 투표
     */
    @Transactional
    public void vote(Long userId, Long branchId) {
        Branch branch = branchRepository.findById(branchId)
                .orElseThrow(EntityNotFoundException::new);

        // 이미 투표했는지 확인
        if (branchVoteRepository.existsByUserIdAndBranchId(userId, branchId)) {
            throw new IllegalStateException("이미 투표하셨습니다.");
        }

        BranchVote vote = new BranchVote(userId, branchId);
        branchVoteRepository.save(vote);

        branch.incrementVoteCount();
    }

    /**
     * 브랜치 투표 취소
     */
    @Transactional
    public void unvote(Long userId, Long branchId) {
        Branch branch = branchRepository.findById(branchId)
                .orElseThrow(EntityNotFoundException::new);

        // 투표했는지 확인
        if (!branchVoteRepository.existsByUserIdAndBranchId(userId, branchId)) {
            throw new IllegalStateException("투표한 적이 없습니다.");
        }

        branchVoteRepository.deleteByUserIdAndBranchId(userId, branchId);

        branch.decrementVoteCount();
    }

    /**
     * 메인 브랜치 조회
     */
    public BranchResponse getMainBranch(Long novelId) {
        Branch mainBranch = branchRepository.findByNovelIdAndIsMainTrue(novelId)
                .orElseThrow(EntityNotFoundException::new);
        return BranchResponse.from(mainBranch);
    }

    private void validateOwnership(Branch branch, Long userId) {
        if (!branch.getAuthor().getId().equals(userId)) {
            throw new UnauthorizedException();
        }
    }
}
