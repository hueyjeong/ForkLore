package io.forklore.domain.user;

import io.forklore.global.common.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.SQLRestriction;

import java.time.LocalDate;

@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Entity
@Table(name = "users")
@SQLRestriction("deleted_at IS NULL")
public class User extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String email;

    private String password;

    @Column(nullable = false, unique = true)
    private String nickname;

    @Column(name = "profile_image_url", columnDefinition = "TEXT")
    private String profileImageUrl;

    @Column(name = "birth_date")
    private LocalDate birthDate;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private UserRole role;

    @Enumerated(EnumType.STRING)
    @Column(name = "auth_provider", nullable = false)
    private AuthProvider authProvider;

    @Column(name = "provider_id")
    private String providerId;

    @Builder
    public User(String email, String password, String nickname, String profileImageUrl, LocalDate birthDate, UserRole role, AuthProvider authProvider, String providerId) {
        this.email = email;
        this.password = password;
        this.nickname = nickname;
        this.profileImageUrl = profileImageUrl;
        this.birthDate = birthDate;
        this.role = role != null ? role : UserRole.READER;
        this.authProvider = authProvider != null ? authProvider : AuthProvider.LOCAL;
        this.providerId = providerId;
    }

    public User update(String nickname, String profileImageUrl) {
        this.nickname = nickname;
        this.profileImageUrl = profileImageUrl;
        return this;
    }

    public void changePassword(String encodedPassword) {
        this.password = encodedPassword;
    }

    public String getRoleKey() {
        return this.role.getKey();
    }
}
