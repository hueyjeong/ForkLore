package io.forklore.security.oauth2.user;

import java.util.Map;

public interface OAuth2UserInfo {
    String getProviderId();
    String getProvider(); // google, kakao
    String getEmail();
    String getName();
    String getImageUrl();
    Map<String, Object> getAttributes();
}
