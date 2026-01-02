package io.forklore.domain.branch;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;

public interface BranchRepository extends JpaRepository<Branch, Long> {

    /**
     * 소설의 메인 브랜치 조회
     */
    Optional<Branch> findByNovelIdAndIsMainTrue(Long novelId);

    /**
     * 소설의 브랜치 목록 조회 (가시성 필터)
     */
    Page<Branch> findByNovelIdAndVisibility(Long novelId, BranchVisibility visibility, Pageable pageable);

    /**
     * 소설의 공개 브랜치 목록 조회 (PUBLIC + LINKED)
     */
    @Query("SELECT b FROM Branch b WHERE b.novel.id = :novelId AND b.visibility IN (:visibilities)")
    Page<Branch> findByNovelIdAndVisibilityIn(
            @Param("novelId") Long novelId,
            @Param("visibilities") java.util.List<BranchVisibility> visibilities,
            Pageable pageable
    );

    /**
     * 작가별 브랜치 목록 조회
     */
    Page<Branch> findByAuthorId(Long authorId, Pageable pageable);

    /**
     * 부모 브랜치의 자식 브랜치 목록 조회
     */
    Page<Branch> findByParentBranchId(Long parentBranchId, Pageable pageable);

    /**
     * 소설의 전체 브랜치 목록 조회 (관리자/작가용)
     */
    Page<Branch> findByNovelId(Long novelId, Pageable pageable);
}
