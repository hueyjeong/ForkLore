package io.forklore.security.jwt;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTVerificationException;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.auth0.jwt.interfaces.JWTVerifier;
import io.forklore.domain.user.UserRole;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.User;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.Collections;
import java.util.Date;
import java.util.List;

@Slf4j
@Component
@RequiredArgsConstructor
public class JwtTokenProvider {

    private final JwtProperties jwtProperties;

    // HMAC256 알고리즘 사용
    private Algorithm getAlgorithm() {
        return Algorithm.HMAC256(jwtProperties.getSecret());
    }

    public String createAccessToken(String email, String role) {
        Instant now = Instant.now();
        return JWT.create()
                .withSubject(email)
                .withClaim("role", role)
                .withIssuedAt(now)
                .withExpiresAt(now.plusMillis(jwtProperties.getAccessTokenExpiration()))
                .sign(getAlgorithm());
    }

    public String createRefreshToken(String email) {
        Instant now = Instant.now();
        return JWT.create()
                .withSubject(email)
                .withIssuedAt(now)
                .withExpiresAt(now.plusMillis(jwtProperties.getRefreshTokenExpiration()))
                .sign(getAlgorithm());
    }

    public boolean validateToken(String token) {
        try {
            JWTVerifier verifier = JWT.require(getAlgorithm()).build();
            verifier.verify(token);
            return true;
        } catch (JWTVerificationException e) {
            log.warn("Invalid JWT Token: {}", e.getMessage());
            return false;
        }
    }

    public Authentication getAuthentication(String token) {
        DecodedJWT decodedJWT = JWT.require(getAlgorithm()).build().verify(token);
        String email = decodedJWT.getSubject();
        String role = decodedJWT.getClaim("role").asString();

        // 역할이 없는 경우 기본값 처리 (Refresh Token 등)
        List<SimpleGrantedAuthority> authorities = role != null 
                ? Collections.singletonList(new SimpleGrantedAuthority(role)) 
                : Collections.emptyList();

        User principal = new User(email, "", authorities);
        return new UsernamePasswordAuthenticationToken(principal, token, authorities);
    }
}
