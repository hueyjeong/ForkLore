package io.forklore.security.oauth2.user;

import io.forklore.domain.user.AuthProvider;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;

import java.util.Map;

public class OAuth2UserInfoFactory {

    public static OAuth2UserInfo getOAuth2UserInfo(String registrationId, Map<String, Object> attributes) {
        if (AuthProvider.GOOGLE.name().equalsIgnoreCase(registrationId)) {
            return new GoogleOAuth2UserInfo(attributes);
        } else if (AuthProvider.KAKAO.name().equalsIgnoreCase(registrationId)) {
            return new KakaoOAuth2UserInfo(attributes);
        } else {
            throw new OAuth2AuthenticationException("Unsupported provider: " + registrationId);
        }
    }
}
