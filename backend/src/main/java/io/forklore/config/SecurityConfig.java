package io.forklore.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

/**
 * Spring Security 설정
 * 현재는 개발 편의를 위해 기본 인증만 활성화
 * TODO: JWT 기반 인증으로 전환 예정
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf(AbstractHttpConfigurer::disable) // 개발 편의를 위해 비활성화
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers(
                                "/api-docs/**",
                                "/swagger-ui/**",
                                "/swagger-ui.html",
                                "/h2-console/**",
                                "/actuator/**"
                        ).permitAll()
                        .anyRequest().permitAll() // 개발 단계에서는 모든 요청 허용
                )
                .headers(headers -> headers
                        .frameOptions(frameOptions -> frameOptions.sameOrigin()) // H2 Console용
                );

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
