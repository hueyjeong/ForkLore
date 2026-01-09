package io.forklore.service.purchase;

import io.forklore.domain.branch.Branch;
import io.forklore.domain.chapter.AccessType;
import io.forklore.domain.chapter.Chapter;
import io.forklore.domain.chapter.ChapterRepository;
import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.purchase.Purchase;
import io.forklore.domain.purchase.PurchaseRepository;
import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.dto.response.PurchaseResponse;
import io.forklore.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;

@ExtendWith(MockitoExtension.class)
class PurchaseServiceTest {

        @InjectMocks
        private PurchaseService purchaseService;

        @Mock
        private PurchaseRepository purchaseRepository;

        @Mock
        private ChapterRepository chapterRepository;

        @Mock
        private UserRepository userRepository;

        private User reader;
        private Chapter chapter;

        @BeforeEach
        void setUp() {
                User author = User.builder()
                                .email("purchase-author@example.com")
                                .password("password")
                                .nickname("작가")
                                .role(UserRole.AUTHOR)
                                .authProvider(AuthProvider.LOCAL)
                                .build();
                ReflectionTestUtils.setField(author, "id", 1L);

                reader = User.builder()
                                .email("purchase-reader@example.com")
                                .password("password")
                                .nickname("독자")
                                .role(UserRole.READER)
                                .authProvider(AuthProvider.LOCAL)
                                .build();
                ReflectionTestUtils.setField(reader, "id", 2L);

                Novel novel = Novel.builder()
                                .author(author)
                                .title("테스트 소설")
                                .genre(Genre.FANTASY)
                                .ageRating(AgeRating.ALL)
                                .allowBranching(true)
                                .build();
                ReflectionTestUtils.setField(novel, "id", 10L);

                Branch branch = Branch.builder()
                                .novel(novel)
                                .author(author)
                                .isMain(true)
                                .name("메인 브랜치")
                                .build();
                ReflectionTestUtils.setField(branch, "id", 100L);

                chapter = Chapter.builder()
                                .branch(branch)
                                .chapterNumber(1)
                                .title("1화")
                                .content("테스트 본문")
                                .accessType(AccessType.SUBSCRIPTION)
                                .price(100)
                                .build();
                ReflectionTestUtils.setField(chapter, "id", 1000L);
        }

        @Test
        @DisplayName("회차 구매 성공")
        void purchase() {
                // given
                given(userRepository.findById(2L)).willReturn(Optional.of(reader));
                given(chapterRepository.findById(1000L)).willReturn(Optional.of(chapter));
                given(purchaseRepository.existsByUserIdAndChapterId(2L, 1000L)).willReturn(false);
                given(purchaseRepository.save(any(Purchase.class))).willAnswer(invocation -> {
                        Purchase p = invocation.getArgument(0);
                        ReflectionTestUtils.setField(p, "id", 5000L);
                        return p;
                });

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
                given(userRepository.findById(2L)).willReturn(Optional.of(reader));
                given(chapterRepository.findById(1000L)).willReturn(Optional.of(chapter));
                given(purchaseRepository.existsByUserIdAndChapterId(2L, 1000L)).willReturn(true);

                // when & then
                assertThatThrownBy(() -> purchaseService.purchase(reader.getId(), chapter.getId()))
                                .isInstanceOf(IllegalStateException.class)
                                .hasMessageContaining("이미 구매한 회차");
        }

        @Test
        @DisplayName("구매 여부 확인")
        void hasPurchased() {
                // given
                given(purchaseRepository.existsByUserIdAndChapterId(2L, 1000L)).willReturn(false);
                // initially not purchased
                assertThat(purchaseService.hasPurchased(reader.getId(), chapter.getId())).isFalse();

                // after purchase
                given(purchaseRepository.existsByUserIdAndChapterId(2L, 1000L)).willReturn(true);
                assertThat(purchaseService.hasPurchased(reader.getId(), chapter.getId())).isTrue();
        }

        @Test
        @DisplayName("구매 목록 조회")
        void getPurchaseList() {
                // given
                Purchase p1 = Purchase.builder().user(reader).chapter(chapter).build();
                given(purchaseRepository.findByUserIdOrderByPurchasedAtDesc(2L)).willReturn(List.of(p1));

                // when
                List<PurchaseResponse> list = purchaseService.getPurchaseList(reader.getId());

                // then
                assertThat(list).hasSize(1);
        }
}
