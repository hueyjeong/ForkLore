package io.forklore.dto.response;

import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserResponse {
    private Long id;
    private String email;
    private String nickname;
    private String profileImageUrl;
    private LocalDate birthDate;
    private UserRole role;
    private AuthProvider authProvider;

    public static UserResponse from(User user) {
        return UserResponse.builder()
                .id(user.getId())
                .email(user.getEmail())
                .nickname(user.getNickname())
                .profileImageUrl(user.getProfileImageUrl())
                .birthDate(user.getBirthDate())
                .role(user.getRole())
                .authProvider(user.getAuthProvider())
                .build();
    }
}
