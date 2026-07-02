package com.platform.auth.security;

import com.platform.auth.config.JwtProperties;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class JwtUtilTest {

    private final JwtUtil jwtUtil = new JwtUtil(new JwtProperties("test-secret-for-unit-tests-only-256bit", 3600));

    @Test
    void generateToken_producesValidToken() {
        String token = jwtUtil.generateToken("sri@example.com", "CANDIDATE");
        assertThat(token).isNotBlank();
        assertThat(jwtUtil.isValid(token)).isTrue();
    }

    @Test
    void extractEmail_returnsOriginalSubject() {
        String token = jwtUtil.generateToken("sri@example.com", "ADMIN");
        assertThat(jwtUtil.extractEmail(token)).isEqualTo("sri@example.com");
    }

    @Test
    void isValid_returnsFalse_forGarbageToken() {
        assertThat(jwtUtil.isValid("not.a.valid.token")).isFalse();
    }

    @Test
    void isValid_returnsFalse_forExpiredToken() {
        JwtUtil shortLived = new JwtUtil(new JwtProperties("test-secret-for-unit-tests-only-256bit", -10));
        String token = shortLived.generateToken("sri@example.com", "CANDIDATE");
        assertThat(shortLived.isValid(token)).isFalse();
    }

    @Test
    void tokenIncludesRoleClaim() {
        String token = jwtUtil.generateToken("sri@example.com", "HR");
        var claims = jwtUtil.parseClaims(token);
        assertThat(claims.get("roles")).asList().contains("HR");
    }
}
