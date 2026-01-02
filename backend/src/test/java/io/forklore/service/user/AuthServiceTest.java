package io.forklore.service.user;

import io.forklore.domain.refresh.RefreshToken;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.dto.request.LoginRequest;
import io.forklore.dto.request.SignUpRequest;
import io.forklore.dto.response.TokenResponse;
import io.forklore.global.error.BusinessException;
import io.forklore.global.error.CommonErrorCode;
import io.forklore.repository.UserRepository;
import io.forklore.repository.refresh.RefreshTokenRepository;
import io.forklore.security.jwt.JwtTokenProvider;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.Instant;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @InjectMocks
    private AuthService authService;

    @Mock
    private UserRepository userRepository;

    @Mock
    private RefreshTokenRepository refreshTokenRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private JwtTokenProvider jwtTokenProvider;

    @Mock
    private AuthenticationManager authenticationManager;

    @Test
    @DisplayName("회원가입 성공")
    void signup_success() {
        // given
        SignUpRequest request = SignUpRequest.builder()
                .email("test@example.com")
                .password("password")
                .nickname("tester")
                .build();

        given(userRepository.existsByEmail(request.getEmail())).willReturn(false);
        given(userRepository.existsByNickname(request.getNickname())).willReturn(false);
        given(passwordEncoder.encode(request.getPassword())).willReturn("encodedPassword");
        given(userRepository.save(any(User.class))).willAnswer(invocation -> invocation.getArgument(0));

        // when
        Long userId = authService.signup(request);

        // then
        assertThat(userId).isNull(); // Repository save mock doesn't set ID, checking invocation success
        verify(userRepository).save(any(User.class));
    }

    @Test
    @DisplayName("회원가입 실패 - 이메일 중복")
    void signup_fail_email_duplicate() {
        // given
        SignUpRequest request = SignUpRequest.builder()
                .email("test@example.com")
                .build();

        given(userRepository.existsByEmail(request.getEmail())).willReturn(true);

        // then
        assertThatThrownBy(() -> authService.signup(request))
                .isInstanceOf(BusinessException.class)
                .hasMessage("이미 존재하는 이메일입니다.");
    }

    @Test
    @DisplayName("로그인 성공")
    void login_success() {
        // given
        LoginRequest request = LoginRequest.builder()
                .email("test@example.com")
                .password("password")
                .build();
        User user = User.builder().email("test@example.com").role(UserRole.READER).build();

        given(authenticationManager.authenticate(any(UsernamePasswordAuthenticationToken.class))).willReturn(null);
        given(userRepository.findByEmail(request.getEmail())).willReturn(Optional.of(user));
        given(jwtTokenProvider.createAccessToken(any(), any())).willReturn("access");
        given(jwtTokenProvider.createRefreshToken(any())).willReturn("refresh");
        
        // when
        TokenResponse response = authService.login(request);

        // then
        assertThat(response.getAccessToken()).isEqualTo("access");
        assertThat(response.getRefreshToken()).isEqualTo("refresh");
        verify(refreshTokenRepository).save(any(RefreshToken.class));
    }
}
