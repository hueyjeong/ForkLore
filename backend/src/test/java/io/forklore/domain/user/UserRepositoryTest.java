package io.forklore.domain.user;

import io.forklore.repository.UserRepository;
import io.forklore.global.config.JpaConfig;
import org.junit.jupiter.api.BeforeEach;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.boot.jpa.test.autoconfigure.TestEntityManager;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ActiveProfiles;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * @DataJpaTest: 슬라이스 테스트로 빠른 실행 + 자동 롤백
 */
@DataJpaTest
@Import(JpaConfig.class)
@ActiveProfiles("common")
class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private TestEntityManager em;

    private User user;

    @BeforeEach
    void setUp() {
        user = User.builder()
                .email("test@example.com")
                .password("password")
                .nickname("tester")
                .role(UserRole.READER)
                .authProvider(AuthProvider.LOCAL)
                .build();
    }

    @Test
    @DisplayName("User 저장 및 조회")
    void saveAndFind() {
        // given
        em.persist(user);
        em.flush();
        em.clear();

        // when
        User foundUser = userRepository.findByEmail("test@example.com").orElseThrow();

        // then
        assertThat(foundUser.getId()).isNotNull();
        assertThat(foundUser.getEmail()).isEqualTo(user.getEmail());
        assertThat(foundUser.getRole()).isEqualTo(UserRole.READER);
        assertThat(foundUser.getCreatedAt()).isNotNull();
    }

    @Test
    @DisplayName("중복 체크 - 이메일 및 닉네임")
    void existsCheck() {
        // given
        em.persist(user);
        em.flush();

        // when & then
        assertThat(userRepository.existsByEmail("test@example.com")).isTrue();
        assertThat(userRepository.existsByNickname("tester")).isTrue();
        assertThat(userRepository.existsByEmail("other@example.com")).isFalse();
        assertThat(userRepository.existsByNickname("other")).isFalse();
    }

}
