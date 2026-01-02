package io.forklore.security.jwt;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTVerificationException;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.auth0.jwt.interfaces.JWTVerifier;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;

import java.time.Instant;

@Slf4j
@Component
@RequiredArgsConstructor
public class JwtTokenProvider {

    private final JwtProperties jwtProperties;
    private final org.springframework.security.core.userdetails.UserDetailsService userDetailsService;

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

        UserDetails userDetails = userDetailsService.loadUserByUsername(email);

        return new UsernamePasswordAuthenticationToken(userDetails, token, userDetails.getAuthorities());
    }
}
