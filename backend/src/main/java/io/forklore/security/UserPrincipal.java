package io.forklore.security;

import io.forklore.domain.user.User;
import lombok.Getter;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.oauth2.core.oidc.OidcIdToken;
import org.springframework.security.oauth2.core.oidc.user.OidcUser;
import org.springframework.security.oauth2.core.user.OAuth2User;

import java.util.Collection;
import java.util.Collections;
import java.util.Map;

@Getter
public class UserPrincipal implements OAuth2User, UserDetails, OidcUser {

    private final User user;
    private final Map<String, Object> attributes;

    public UserPrincipal(User user, Map<String, Object> attributes) {
        this.user = user;
        this.attributes = attributes;
    }

    @Override
    public Map<String, Object> getAttributes() {
        return attributes;
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return Collections.singletonList(new SimpleGrantedAuthority(user.getRoleKey()));
    }

    @Override
    public String getPassword() {
        return user.getPassword(); // Assuming password exists (might be null for OAuth2 only)
    }

    @Override
    public String getUsername() {
        return user.getEmail();
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        return true;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        return true;
    }

    @Override
    public String getName() {
        return user.getId().toString();
    }

    // OidcUser methods
    @Override
    public Map<String, Object> getClaims() {
        return null; // Handle if OIDC is strictly needed
    }

    @Override
    public OidcIdToken getIdToken() {
        return null; // Handle if OIDC is strictly needed
    }

    @Override
    public org.springframework.security.oauth2.core.oidc.OidcUserInfo getUserInfo() {
        return null; // Handle if OIDC is strictly needed
    }
}
