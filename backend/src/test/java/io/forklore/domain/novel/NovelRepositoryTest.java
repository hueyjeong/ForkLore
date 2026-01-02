package io.forklore.domain.novel;

import io.forklore.domain.user.User;
import io.forklore.repository.UserRepository;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;



import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@Transactional
public class NovelRepositoryTest {

    @Autowired
    private NovelRepository novelRepository;

    @Autowired
    private UserRepository userRepository;

    @Test
    @DisplayName("Novel 저장 및 조회 테스트")
    void saveAndFindNovel() {
        // given
        User author = User.builder()
                .email("author@example.com")
                .nickname("NovelAuthor")
                .password("password")
                .build();
        userRepository.save(author);

        Novel novel = Novel.builder()
                .author(author)
                .title("테스트 소설")
                .description("테스트 설명입니다.")
                .genre(Genre.ALTERNATIVE_HISTORY)
                .ageRating(AgeRating.R15)
                .build();

        // when
        Novel savedNovel = novelRepository.save(novel);

        // then
        assertThat(savedNovel.getId()).isNotNull();
        assertThat(savedNovel.getTitle()).isEqualTo("테스트 소설");
        assertThat(savedNovel.getGenre()).isEqualTo(Genre.ALTERNATIVE_HISTORY);
        assertThat(savedNovel.getAgeRating()).isEqualTo(AgeRating.R15);
        assertThat(savedNovel.getStatus()).isEqualTo(NovelStatus.ONGOING); // Default check
        assertThat(savedNovel.getAuthor().getNickname()).isEqualTo("NovelAuthor");
    }
}
