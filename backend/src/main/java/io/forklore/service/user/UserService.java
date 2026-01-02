package io.forklore.service.user;

import io.forklore.domain.user.User;
import io.forklore.dto.request.UpdatePasswordRequest;
import io.forklore.dto.request.UpdateProfileRequest;
import io.forklore.dto.response.UserResponse;
import io.forklore.global.error.BusinessException;
import io.forklore.global.error.CommonErrorCode;
import io.forklore.global.error.EntityNotFoundException;
import io.forklore.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public UserResponse getProfile(Long userId) {
        User user = findUserOrThrow(userId);
        return UserResponse.from(user);
    }

    @Transactional
    public UserResponse updateProfile(Long userId, UpdateProfileRequest request) {
        User user = findUserOrThrow(userId);
        user.update(request.getNickname(), request.getProfileImageUrl());
        return UserResponse.from(user);
    }

    @Transactional
    public void updatePassword(Long userId, UpdatePasswordRequest request) {
        User user = findUserOrThrow(userId);
        
        if (!passwordEncoder.matches(request.getCurrentPassword(), user.getPassword())) {
            throw new BusinessException(CommonErrorCode.INVALID_INPUT_VALUE);
        }

        user.changePassword(passwordEncoder.encode(request.getNewPassword()));
    }

    private User findUserOrThrow(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new EntityNotFoundException());
    }
}
