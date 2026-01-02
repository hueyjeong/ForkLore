package io.forklore.domain.user;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;


import static org.assertj.core.api.Assertions.assertThat;

class UserTest {

    @Test
    @DisplayName("User 생성 테스트 - 기본값 확인")
    void createUser() {
        // given
        String email = "test@example.com";
        String password = "password";
        String nickname = "tester";

        // when
        User user = User.builder()
                .email(email)
                .password(password)
                .nickname(nickname)
                .build();

        // then
        assertThat(user.getEmail()).isEqualTo(email);
        assertThat(user.getPassword()).isEqualTo(password);
        assertThat(user.getNickname()).isEqualTo(nickname);
        assertThat(user.getRole()).isEqualTo(UserRole.READER); // Default
        assertThat(user.getAuthProvider()).isEqualTo(AuthProvider.LOCAL); // Default
    }

    @Test
    @DisplayName("User 정보 수정 테스트")
    void updateUser() {
        // given
        User user = User.builder()
                .email("test@example.com")
                .nickname("old")
                .profileImageUrl("old.jpg")
                .build();

        // when
        user.update("new", "new.jpg");

        // then
        assertThat(user.getNickname()).isEqualTo("new");
        assertThat(user.getProfileImageUrl()).isEqualTo("new.jpg");
    }
}
