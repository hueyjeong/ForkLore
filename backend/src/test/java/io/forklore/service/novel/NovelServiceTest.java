package io.forklore.service.novel;

import io.forklore.domain.novel.AgeRating;
import io.forklore.domain.novel.Genre;
import io.forklore.domain.novel.Novel;
import io.forklore.domain.novel.NovelRepository;
import io.forklore.domain.novel.NovelStatus;
import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.dto.request.NovelCreateRequest;
import io.forklore.dto.request.NovelUpdateRequest;
import io.forklore.dto.response.NovelResponse;
import io.forklore.dto.response.NovelSummaryResponse;
import io.forklore.global.error.EntityNotFoundException;
import io.forklore.global.error.UnauthorizedException;
import io.forklore.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;

import java.lang.reflect.Field;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

/**
 * NovelService Unit Test
 * - Mockito를 사용한 빠른 단위 테스트
 * - Reflection을 사용하여 ID 및 private 필드 직접 설정
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("NovelService Unit Test")
class NovelServiceTest {

    @Mock
    private NovelRepository novelRepository;

    @Mock
    private UserRepository userRepository;

    @Mock
    private io.forklore.service.branch.BranchService branchService;

    @InjectMocks
    private NovelService novelService;

    private User author;
    private User otherUser;
    private Novel novel;

    @BeforeEach
    void setUp() throws Exception {
        author = User.builder()
                .email("author@example.com")
                .password("encoded-password")
                .nickname("작가")
                .role(UserRole.AUTHOR)
                .authProvider(AuthProvider.LOCAL)
                .build();
        setId(author, 1L);

        otherUser = User.builder()
                .email("other@example.com")
                .password("encoded-password")
                .nickname("일반인")
                .role(UserRole.READER)
                .authProvider(AuthProvider.LOCAL)
                .build();
        setId(otherUser, 2L);

        novel = Novel.builder()
                .author(author)
                .title("테스트 소설")
                .description("테스트 소설 설명")
                .genre(Genre.FANTASY)
                .ageRating(AgeRating.ALL)
                .allowBranching(false)
                .build();
        setId(novel, 1L);
        setField(novel, "status", NovelStatus.ONGOING);
    }

    private void setId(Object entity, Long id) throws Exception {
        Field idField = entity.getClass().getDeclaredField("id");
        idField.setAccessible(true);
        idField.set(entity, id);
    }

    private void setField(Object entity, String fieldName, Object value) throws Exception {
        Field field = entity.getClass().getDeclaredField(fieldName);
        field.setAccessible(true);
        field.set(entity, value);
    }

    @Test
    @DisplayName("소설 생성 성공")
    void createNovel() {
        // given
        NovelCreateRequest request = NovelCreateRequest.builder()
                .title("새로운 소설")
                .description("새로운 소설 설명")
                .genre(Genre.FANTASY)
                .ageRating(AgeRating.ALL)
                .allowBranching(true)
                .build();

        given(userRepository.findById(1L)).willReturn(Optional.of(author));
        given(novelRepository.save(any(Novel.class))).willReturn(novel);

        // when
        NovelResponse response = novelService.create(1L, request);

        // then
        assertThat(response).isNotNull();
        verify(userRepository).findById(1L);
        verify(novelRepository).save(any(Novel.class));
    }

    @Test
    @DisplayName("소설 생성 실패 - 작가가 아닌 사용자")
    void createNovelFailsWhenNotAuthor() {
        // given
        NovelCreateRequest request = NovelCreateRequest.builder()
                .title("새로운 소설")
                .description("설명")
                .genre(Genre.FANTASY)
                .ageRating(AgeRating.ALL)
                .allowBranching(true)
                .build();

        given(userRepository.findById(2L)).willReturn(Optional.of(otherUser));

        // when & then
        assertThatThrownBy(() -> novelService.create(2L, request))
                .isInstanceOf(UnauthorizedException.class);
    }

    @Test
    @DisplayName("소설 목록 조회 성공")
    void getNovelList() {
        // given
        Pageable pageable = PageRequest.of(0, 20);
        Page<Novel> novelPage = new PageImpl<>(List.of(novel));

        given(novelRepository.findAll(any(Pageable.class))).willReturn(novelPage);

        // when
        Page<NovelSummaryResponse> result = novelService.getList(null, null, pageable);

        // then
        assertThat(result).isNotNull();
        assertThat(result.getContent()).hasSize(1);
    }

    @Test
    @DisplayName("소설 상세 조회 성공")
    void getNovelDetail() {
        // given
        given(novelRepository.findById(1L)).willReturn(Optional.of(novel));

        // when
        NovelResponse response = novelService.getDetail(1L);

        // then
        assertThat(response).isNotNull();
        assertThat(response.getTitle()).isEqualTo("테스트 소설");
    }

    @Test
    @DisplayName("소설 상세 조회 실패 - 존재하지 않는 소설")
    void getNovelDetailNotFound() {
        // given
        given(novelRepository.findById(999L)).willReturn(Optional.empty());

        // when & then
        assertThatThrownBy(() -> novelService.getDetail(999L))
                .isInstanceOf(EntityNotFoundException.class);
    }

    @Test
    @DisplayName("소설 수정 성공")
    void updateNovel() {
        // given
        NovelUpdateRequest request = NovelUpdateRequest.builder()
                .title("수정된 제목")
                .description("수정된 설명")
                .build();

        given(userRepository.findById(1L)).willReturn(Optional.of(author));
        given(novelRepository.findById(1L)).willReturn(Optional.of(novel));

        // when
        NovelResponse response = novelService.update(1L, 1L, request);

        // then
        assertThat(response).isNotNull();
        assertThat(novel.getTitle()).isEqualTo("수정된 제목");
    }

    @Test
    @DisplayName("소설 수정 실패 - 작가가 아닌 사용자")
    void updateNovelFailsWhenNotAuthor() {
        // given
        NovelUpdateRequest request = NovelUpdateRequest.builder()
                .title("수정된 제목")
                .build();

        given(userRepository.findById(2L)).willReturn(Optional.of(otherUser));
        given(novelRepository.findById(1L)).willReturn(Optional.of(novel));

        // when & then
        assertThatThrownBy(() -> novelService.update(2L, 1L, request))
                .isInstanceOf(UnauthorizedException.class);
    }

    @Test
    @DisplayName("소설 삭제 성공")
    void deleteNovel() {
        // given
        given(userRepository.findById(1L)).willReturn(Optional.of(author));
        given(novelRepository.findById(1L)).willReturn(Optional.of(novel));

        // when
        novelService.delete(1L, 1L);

        // then
        verify(novelRepository).delete(novel);
    }

    @Test
    @DisplayName("소설 삭제 실패 - 작가가 아닌 사용자")
    void deleteNovelFailsWhenNotAuthor() {
        // given
        given(userRepository.findById(2L)).willReturn(Optional.of(otherUser));
        given(novelRepository.findById(1L)).willReturn(Optional.of(novel));

        // when & then
        assertThatThrownBy(() -> novelService.delete(2L, 1L))
                .isInstanceOf(UnauthorizedException.class);
    }
}
