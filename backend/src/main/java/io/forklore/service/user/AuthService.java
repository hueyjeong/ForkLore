package io.forklore.service.user;

import io.forklore.domain.refresh.RefreshToken;
import io.forklore.domain.user.User;
import io.forklore.dto.request.LoginRequest;
import io.forklore.dto.request.SignUpRequest;
import io.forklore.dto.request.TokenRefreshRequest;
import io.forklore.dto.response.TokenResponse;
import io.forklore.global.error.BusinessException;
import io.forklore.global.error.CommonErrorCode;
import io.forklore.global.error.EntityNotFoundException;
import io.forklore.repository.UserRepository;
import io.forklore.repository.refresh.RefreshTokenRepository;
import io.forklore.security.jwt.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final RefreshTokenRepository refreshTokenRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;
    private final AuthenticationManager authenticationManager;

    @Transactional
    public Long signup(SignUpRequest request) {
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new BusinessException("이미 존재하는 이메일입니다.", CommonErrorCode.INVALID_INPUT_VALUE);
        }
        if (userRepository.existsByNickname(request.getNickname())) {
            throw new BusinessException("이미 존재하는 닉네임입니다.", CommonErrorCode.INVALID_INPUT_VALUE);
        }

        User user = request.toEntity(passwordEncoder);
        return userRepository.save(user).getId();
    }

    @Transactional
    public TokenResponse login(LoginRequest request) {
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getEmail(), request.getPassword())
        );

        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new EntityNotFoundException("사용자를 찾을 수 없습니다."));

        String accessToken = jwtTokenProvider.createAccessToken(user.getEmail(), user.getRoleKey());
        String refreshToken = jwtTokenProvider.createRefreshToken(user.getEmail());

        // Refresh Token 저장 (기존 토큰 있으면 삭제 후 저장, 혹은 업데이트)
        refreshTokenRepository.deleteByUser(user);
        refreshTokenRepository.save(RefreshToken.builder()
                .user(user)
                .token(refreshToken)
                .expiryDate(Instant.now().plusMillis(604800000L)) // 7일 (하드코딩 개선 필요하지만 일단 진행)
                .build());

        return TokenResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .expiresIn(3600L) // 1시간
                .build();
    }

    @Transactional
    public TokenResponse refresh(TokenRefreshRequest request) {
        String token = request.getRefreshToken();
        
        if (!jwtTokenProvider.validateToken(token)) {
             throw new BusinessException("유효하지 않은 Refresh Token입니다.", CommonErrorCode.INVALID_INPUT_VALUE);
        }

        RefreshToken refreshToken = refreshTokenRepository.findByToken(token)
                .orElseThrow(() -> new EntityNotFoundException("Refresh Token을 찾을 수 없습니다."));

        User user = refreshToken.getUser();
        String newAccessToken = jwtTokenProvider.createAccessToken(user.getEmail(), user.getRoleKey());
        
        return TokenResponse.builder()
                .accessToken(newAccessToken)
                .refreshToken(token) // Rotate 하지 않고 그대로 반환 (정책에 따라 다름)
                .expiresIn(3600L)
                .build();
    }
}
