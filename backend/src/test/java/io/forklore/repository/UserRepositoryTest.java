package io.forklore.repository;

import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.test.context.ActiveProfiles;

import java.time.LocalDateTime;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@Transactional
@ActiveProfiles("common")
class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

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
        User savedUser = userRepository.save(user);

        // when
        User foundUser = userRepository.findByEmail("test@example.com").orElseThrow();

        // then
        assertThat(foundUser.getId()).isNotNull();
        assertThat(foundUser.getEmail()).isEqualTo(savedUser.getEmail());
        assertThat(foundUser.getRole()).isEqualTo(UserRole.READER);
        assertThat(foundUser.getCreatedAt()).isNotNull();
    }

    @Test
    @DisplayName("중복 체크 - 이메일 및 닉네임")
    void existsCheck() {
        // given
        userRepository.save(user);

        // then
        assertThat(userRepository.existsByEmail("test@example.com")).isTrue();
        assertThat(userRepository.existsByNickname("tester")).isTrue();
        assertThat(userRepository.existsByEmail("other@example.com")).isFalse();
    }

    @Autowired
    private jakarta.persistence.EntityManager em;

    @Test
    @DisplayName("Soft Delete 확인 - @SQLRestriction 동작")
    void softDelete() {
        // given
        User savedUser = userRepository.save(user);

        // when
        savedUser.setDeletedAt(LocalDateTime.now());
        userRepository.save(savedUser);
        userRepository.flush(); // DB 반영
        em.clear(); // 영속성 컨텍스트 비우기

        // then
        // @SQLRestriction으로 인해 조회되지 않아야 함
        assertThat(userRepository.findByEmail("test@example.com")).isEmpty();
        assertThat(userRepository.findById(savedUser.getId())).isEmpty();
    }
}
