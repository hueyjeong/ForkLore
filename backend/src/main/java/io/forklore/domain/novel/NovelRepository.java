package io.forklore.domain.novel;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface NovelRepository extends JpaRepository<Novel, Long> {
    
    Page<Novel> findByGenre(Genre genre, Pageable pageable);
    
    Page<Novel> findByStatus(NovelStatus status, Pageable pageable);
    
    Page<Novel> findByAuthorId(Long authorId, Pageable pageable);
    
    Page<Novel> findByGenreAndStatus(Genre genre, NovelStatus status, Pageable pageable);
}
