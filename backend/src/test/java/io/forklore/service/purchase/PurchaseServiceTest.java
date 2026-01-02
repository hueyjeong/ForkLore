package io.forklore.service.purchase;

import io.forklore.domain.branch.Branch;
import io.forklore.domain.branch.BranchRepository;
import io.forklore.domain.branch.BranchType;
import io.forklore.domain.branch.BranchVisibility;
import io.forklore.domain.chapter.AccessType;
import io.forklore.domain.chapter.Chapter;
import io.forklore.domain.chapter.ChapterRepository;
import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.novel.NovelRepository;
import io.forklore.domain.purchase.PurchaseRepository;
import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.dto.response.PurchaseResponse;
import io.forklore.repository.UserRepository;
import jakarta.persistence.EntityManager;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

@SpringBootTest
@Transactional
@ActiveProfiles("common")
class PurchaseServiceTest {

    @Autowired
    private PurchaseService purchaseService;

    @Autowired
    private PurchaseRepository purchaseRepository;

    @Autowired
    private ChapterRepository chapterRepository;

    @Autowired
    private BranchRepository branchRepository;

    @Autowired
    private NovelRepository novelRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private EntityManager em;

    private User reader;
    private User author;
    private Novel novel;
    private Branch branch;
    private Chapter chapter;

    @BeforeEach
    void setUp() {
        author = User.builder()
                .email("purchase-author@example.com")
                .password("password")
                .nickname("작가")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(author);

        reader = User.builder()
                .email("purchase-reader@example.com")
                .password("password")
                .nickname("독자")
                .role(UserRole.READER)
                .authProvider(AuthProvider.LOCAL)
                .build();
        userRepository.save(reader);

        novel = Novel.builder()
                .author(author)
                .title("테스트 소설")
                .genre(Genre.FANTASY)
                .ageRating(AgeRating.ALL)
                .allowBranching(true)
                .build();
        novelRepository.save(novel);

        branch = Branch.builder()
                .novel(novel)
                .author(author)
                .isMain(true)
                .name("메인 브랜치")
                .branchType(BranchType.MAIN)
                .visibility(BranchVisibility.PUBLIC)
                .build();
        branchRepository.save(branch);

        chapter = Chapter.builder()
                .branch(branch)
                .chapterNumber(1)
                .title("1화")
                .content("테스트 본문")
                .contentHtml("<p>테스트 본문</p>")
                .wordCount(10)
                .accessType(AccessType.SUBSCRIPTION)
                .price(100)
                .build();
        chapterRepository.save(chapter);
    }

    @Test
    @DisplayName("회차 구매 성공")
    void purchase() {
        // when
        PurchaseResponse response = purchaseService.purchase(reader.getId(), chapter.getId());

        // then
        assertThat(response.getChapterId()).isEqualTo(chapter.getId());
        assertThat(response.getChapterTitle()).isEqualTo("1화");
        assertThat(response.getPrice().intValue()).isEqualTo(100);
    }

    @Test
    @DisplayName("중복 구매 방지")
    void preventDuplicatePurchase() {
        // given
        purchaseService.purchase(reader.getId(), chapter.getId());
        em.flush();
        em.clear();

        // when & then
        assertThatThrownBy(() -> purchaseService.purchase(reader.getId(), chapter.getId()))
                .isInstanceOf(IllegalStateException.class)
                .hasMessageContaining("이미 구매한 회차");
    }

    @Test
    @DisplayName("구매 여부 확인")
    void hasPurchased() {
        // initially not purchased
        assertThat(purchaseService.hasPurchased(reader.getId(), chapter.getId())).isFalse();

        // after purchase
        purchaseService.purchase(reader.getId(), chapter.getId());
        assertThat(purchaseService.hasPurchased(reader.getId(), chapter.getId())).isTrue();
    }

    @Test
    @DisplayName("구매 목록 조회")
    void getPurchaseList() {
        // given
        Chapter chapter2 = chapterRepository.save(Chapter.builder()
                .branch(branch)
                .chapterNumber(2)
                .title("2화")
                .content("본문2")
                .contentHtml("<p>본문2</p>")
                .wordCount(10)
                .accessType(AccessType.SUBSCRIPTION)
                .price(100)
                .build());

        purchaseService.purchase(reader.getId(), chapter.getId());
        purchaseService.purchase(reader.getId(), chapter2.getId());
        em.flush();
        em.clear();

        // when
        List<PurchaseResponse> list = purchaseService.getPurchaseList(reader.getId());

        // then
        assertThat(list).hasSize(2);
    }
}
