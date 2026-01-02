package io.forklore.service.branch;

import io.forklore.domain.branch.*;
import io.forklore.domain.user.User;
import io.forklore.dto.response.LinkRequestResponse;
import io.forklore.global.error.EntityNotFoundException;
import io.forklore.global.error.UnauthorizedException;
import io.forklore.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class BranchLinkService {

    private final BranchRepository branchRepository;
    private final BranchLinkRequestRepository linkRequestRepository;
    private final UserRepository userRepository;

    /**
     * 연결 요청 생성
     */
    @Transactional
    public LinkRequestResponse requestLink(Long branchId, Long requesterId, String message) {
        Branch branch = branchRepository.findById(branchId)
                .orElseThrow(EntityNotFoundException::new);

        // 본인 브랜치인지 확인
        if (!branch.getAuthor().getId().equals(requesterId)) {
            throw new UnauthorizedException("본인의 브랜치만 연결 요청할 수 있습니다.");
        }

        // 메인 브랜치는 연결 요청 불가
        if (branch.isMain()) {
            throw new IllegalStateException("메인 브랜치는 연결 요청할 수 없습니다.");
        }

        // 이미 LINKED 상태인 경우
        if (branch.getVisibility() == BranchVisibility.LINKED) {
            throw new IllegalStateException("이미 연결된 브랜치입니다.");
        }

        // 대기 중인 요청이 있는지 확인
        if (linkRequestRepository.existsByBranchIdAndStatus(branchId, LinkRequestStatus.PENDING)) {
            throw new IllegalStateException("이미 대기 중인 연결 요청이 있습니다.");
        }

        BranchLinkRequest request = BranchLinkRequest.builder()
                .branch(branch)
                .requestMessage(message)
                .build();

        BranchLinkRequest saved = linkRequestRepository.save(request);
        return LinkRequestResponse.from(saved);
    }

    /**
     * 연결 요청 승인 (원작 작가만)
     */
    @Transactional
    public LinkRequestResponse approveLink(Long requestId, Long reviewerId, String comment) {
        BranchLinkRequest request = linkRequestRepository.findById(requestId)
                .orElseThrow(EntityNotFoundException::new);

        validateReviewerPermission(request, reviewerId);
        validatePendingStatus(request);

        User reviewer = userRepository.findById(reviewerId)
                .orElseThrow(EntityNotFoundException::new);

        request.approve(reviewer, comment);

        return LinkRequestResponse.from(request);
    }

    /**
     * 연결 요청 거절 (원작 작가만)
     */
    @Transactional
    public LinkRequestResponse rejectLink(Long requestId, Long reviewerId, String comment) {
        BranchLinkRequest request = linkRequestRepository.findById(requestId)
                .orElseThrow(EntityNotFoundException::new);

        validateReviewerPermission(request, reviewerId);
        validatePendingStatus(request);

        User reviewer = userRepository.findById(reviewerId)
                .orElseThrow(EntityNotFoundException::new);

        request.reject(reviewer, comment);

        return LinkRequestResponse.from(request);
    }

    /**
     * 연결 요청 상세 조회
     */
    public LinkRequestResponse getRequest(Long requestId) {
        BranchLinkRequest request = linkRequestRepository.findById(requestId)
                .orElseThrow(EntityNotFoundException::new);
        return LinkRequestResponse.from(request);
    }

    /**
     * 리뷰어 권한 검증 (원작 작가인지)
     */
    private void validateReviewerPermission(BranchLinkRequest request, Long reviewerId) {
        Long novelAuthorId = request.getBranch().getNovel().getAuthor().getId();
        if (!novelAuthorId.equals(reviewerId)) {
            throw new UnauthorizedException("원작 작가만 연결 요청을 처리할 수 있습니다.");
        }
    }

    /**
     * 대기 상태 검증
     */
    private void validatePendingStatus(BranchLinkRequest request) {
        if (!request.isPending()) {
            throw new IllegalStateException("이미 처리된 요청입니다.");
        }
    }
}
