package io.forklore.service.user;

import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.dto.request.UpdatePasswordRequest;
import io.forklore.dto.request.UpdateProfileRequest;
import io.forklore.dto.response.UserResponse;
import io.forklore.global.error.BusinessException;
import io.forklore.global.error.CommonErrorCode;
import io.forklore.repository.UserRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.LocalDate;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @InjectMocks
    private UserService userService;

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Test
    @DisplayName("프로필 조회 성공")
    void getProfile_success() {
        // given
        User user = User.builder()
                .email("test@email.com")
                .nickname("Tester")
                .role(UserRole.READER)
                .authProvider(AuthProvider.LOCAL)
                .build();
        
        given(userRepository.findById(1L)).willReturn(Optional.of(user));

        // when
        UserResponse result = userService.getProfile(1L);

        // then
        assertThat(result.getEmail()).isEqualTo("test@email.com");
        assertThat(result.getNickname()).isEqualTo("Tester");
    }

    @Test
    @DisplayName("프로필 수정 성공")
    void updateProfile_success() {
        // given
        User user = User.builder()
                .email("test@email.com")
                .nickname("OldNick")
                .build();
        given(userRepository.findById(1L)).willReturn(Optional.of(user));

        UpdateProfileRequest request = new UpdateProfileRequest("NewNick", "http://new.img");

        // when
        UserResponse result = userService.updateProfile(1L, request);

        // then
        assertThat(result.getNickname()).isEqualTo("NewNick");
        assertThat(result.getProfileImageUrl()).isEqualTo("http://new.img");
    }

    @Test
    @DisplayName("비밀번호 변경 성공")
    void updatePassword_success() {
        // given
        User user = User.builder()
                .email("test@email.com")
                .password("encodedOldPw")
                .build();
        given(userRepository.findById(1L)).willReturn(Optional.of(user));
        
        UpdatePasswordRequest request = new UpdatePasswordRequest("oldPw", "newPw");
        
        given(passwordEncoder.matches("oldPw", "encodedOldPw")).willReturn(true);
        given(passwordEncoder.encode("newPw")).willReturn("encodedNewPw");

        // when
        userService.updatePassword(1L, request);

        // then
        assertThat(user.getPassword()).isEqualTo("encodedNewPw");
        verify(passwordEncoder).encode("newPw");
    }
    
    @Test
    @DisplayName("비밀번호 변경 실패 - 현재 비밀번호 불일치")
    void updatePassword_fail_wrongCurrentPassword() {
        // given
        User user = User.builder()
                .email("test@email.com")
                .password("encodedOldPw")
                .build();
        given(userRepository.findById(1L)).willReturn(Optional.of(user)); // Mocking 추가

        UpdatePasswordRequest request = new UpdatePasswordRequest("wrongPw", "newPw");
        
        given(passwordEncoder.matches("wrongPw", "encodedOldPw")).willReturn(false);

        // when & then
        assertThatThrownBy(() -> userService.updatePassword(1L, request))
                .isInstanceOf(BusinessException.class)
                .hasFieldOrPropertyWithValue("errorCode", CommonErrorCode.INVALID_INPUT_VALUE);
    }
}
