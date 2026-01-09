package io.forklore.security.oauth2;

import io.forklore.domain.user.AuthProvider;
import io.forklore.domain.user.User;
import io.forklore.domain.user.UserRole;
import io.forklore.repository.UserRepository;
import io.forklore.security.UserPrincipal;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.core.AuthorizationGrantType;
import org.springframework.security.oauth2.core.user.OAuth2User;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class CustomOAuth2UserServiceTest {

    @InjectMocks
    private CustomOAuth2UserService customOAuth2UserService;

    @Mock
    private UserRepository userRepository;

    @Mock
    private OAuth2UserRequest oAuth2UserRequest;

    @Mock
    private OAuth2User oAuth2User;

    @Test
    @DisplayName("Google 로그인 - 신규 유저 생성")
    void process_Google_NewUser() {
        // given
        ClientRegistration clientRegistration = ClientRegistration.withRegistrationId("google")
                .authorizationGrantType(AuthorizationGrantType.AUTHORIZATION_CODE)
                .clientId("clientId")
                .redirectUri("redirectUri")
                .authorizationUri("authUri")
                .tokenUri("tokenUri")
                .userInfoUri("userInfoUri") // Required for builder?
                .userNameAttributeName("sub")
                .build();

        given(oAuth2UserRequest.getClientRegistration()).willReturn(clientRegistration);

        Map<String, Object> attributes = new HashMap<>();
        attributes.put("sub", "12345");
        attributes.put("name", "Test User");
        attributes.put("email", "test@gmail.com");
        attributes.put("picture", "http://image.com");

        given(oAuth2User.getAttributes()).willReturn(attributes);
        given(userRepository.findByEmail("test@gmail.com")).willReturn(Optional.empty());

        User savedUser = User.builder()
                .email("test@gmail.com")
                .nickname("Test User")
                .role(UserRole.READER)
                .authProvider(AuthProvider.GOOGLE)
                .providerId("12345")
                .build();
        given(userRepository.save(any(User.class))).willReturn(savedUser);

        // when
        OAuth2User result = customOAuth2UserService.process(oAuth2UserRequest, oAuth2User);

        // then
        assertThat(result).isInstanceOf(UserPrincipal.class);
        UserPrincipal principal = (UserPrincipal) result;
        assertThat(principal.getUser().getEmail()).isEqualTo("test@gmail.com");
        assertThat(principal.getUser().getAuthProvider()).isEqualTo(AuthProvider.GOOGLE);

        verify(userRepository).save(any(User.class));
    }
}
