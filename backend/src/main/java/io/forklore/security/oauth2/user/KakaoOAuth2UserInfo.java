package io.forklore.security.oauth2.user;

import java.util.Map;

public class KakaoOAuth2UserInfo implements OAuth2UserInfo {

    private Map<String, Object> attributes;
    private Map<String, Object> attributesAccount;
    private Map<String, Object> attributesProfile;

    @SuppressWarnings("unchecked")
    public KakaoOAuth2UserInfo(Map<String, Object> attributes) {
        this.attributes = attributes;
        this.attributesAccount = (Map<String, Object>) attributes.get("kakao_account");
        this.attributesProfile = (Map<String, Object>) attributesAccount.get("profile");
    }

    @Override
    public String getProviderId() {
        return String.valueOf(attributes.get("id"));
    }

    @Override
    public String getProvider() {
        return "kakao";
    }

    @Override
    public String getEmail() {
        return (String) attributesAccount.get("email");
    }

    @Override
    public String getName() {
        return (String) attributesProfile.get("nickname"); // Kakao uses nickname in profile
    }

    @Override
    public String getImageUrl() {
        return (String) attributesProfile.get("profile_image_url");
    }

    @Override
    public Map<String, Object> getAttributes() {
        return attributes;
    }
}
