package io.forklore.controller;

import io.forklore.dto.request.UpdatePasswordRequest;
import io.forklore.dto.request.UpdateProfileRequest;
import io.forklore.dto.response.UserResponse;
import io.forklore.global.common.ApiResponse;
import io.forklore.security.UserPrincipal;
import io.forklore.service.user.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/me")
    public ApiResponse<UserResponse> getMyProfile(@AuthenticationPrincipal UserPrincipal userPrincipal) {
        UserResponse response = userService.getProfile(userPrincipal.getId());
        return ApiResponse.success(response);
    }

    @PatchMapping("/me")
    public ApiResponse<UserResponse> updateProfile(
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @Valid @RequestBody UpdateProfileRequest request) {
        UserResponse response = userService.updateProfile(userPrincipal.getId(), request);
        return ApiResponse.success(response);
    }

    @PostMapping("/me/password")
    public ApiResponse<Void> updatePassword(
            @AuthenticationPrincipal UserPrincipal userPrincipal,
            @Valid @RequestBody UpdatePasswordRequest request) {
        userService.updatePassword(userPrincipal.getId(), request);
        return ApiResponse.success();
    }
}
