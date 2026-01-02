package io.forklore.security.oauth2;

import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.repository.UserRepository;
import io.forklore.security.UserPrincipal;
import io.forklore.security.oauth2.user.GoogleOAuth2UserInfo;
import io.forklore.security.oauth2.user.KakaoOAuth2UserInfo;
import io.forklore.security.oauth2.user.OAuth2UserInfo;
import io.forklore.security.oauth2.user.OAuth2UserInfoFactory;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserService;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class CustomOAuth2UserService implements OAuth2UserService<OAuth2UserRequest, OAuth2User> {

    private final UserRepository userRepository;
    
    // Delegate set to default, can be overridden for testing? 
    // Ideally should be injected but DefaultOAuth2UserService doesn't need injection usually.
    // For TDD, I will wrap it. 
    // But for now, let's keep it simple and instantiate. 
    // To enable testing, I will use a protected method or field injection if needed, 
    // but constructor injection of delegate is cleanest if I register it as a bean. 
    // However, configuring circular deps might be an issue if not careful.
    // Let's just use "new" for now and if test fails, refactor.

    @Override
    @Transactional
    public OAuth2User loadUser(OAuth2UserRequest userRequest) throws OAuth2AuthenticationException {
        OAuth2UserService<OAuth2UserRequest, OAuth2User> delegate = new DefaultOAuth2UserService();
        OAuth2User oAuth2User = delegate.loadUser(userRequest);

        return process(userRequest, oAuth2User);
    }
    
    // Separated for testing (if I want to test logic without network)
    public OAuth2User process(OAuth2UserRequest userRequest, OAuth2User oAuth2User) {
        String registrationId = userRequest.getClientRegistration().getRegistrationId();
        Map<String, Object> attributes = oAuth2User.getAttributes();

        OAuth2UserInfo userInfo = OAuth2UserInfoFactory.getOAuth2UserInfo(registrationId, attributes);
        
        // Save or Update User
        User user = saveOrUpdate(userInfo, registrationId);
        
        return new UserPrincipal(user, attributes);
    }

    private User saveOrUpdate(OAuth2UserInfo userInfo, String registrationId) {
        AuthProvider provider = AuthProvider.valueOf(registrationId.toUpperCase());
        Optional<User> userOptional = userRepository.findByEmail(userInfo.getEmail());
        
        if (userOptional.isPresent()) {
            User user = userOptional.get();
            // 프로필 업데이트 로직 (필요 시)
            // user.update(userInfo.getName(), userInfo.getImageUrl());
            // return userRepository.save(user);
            return user;
        } else {
            User newUser = User.builder()
                    .email(userInfo.getEmail())
                    .nickname(userInfo.getName())
                    .role(UserRole.READER)
                    .authProvider(provider)
                    .providerId(userInfo.getProviderId())
                    .profileImageUrl(userInfo.getImageUrl())
                    .build();
            return userRepository.save(newUser);
        }
    }
}
