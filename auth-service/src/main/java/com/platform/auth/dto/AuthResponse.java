package com.platform.auth.dto;

public record AuthResponse(
        String token,
        String tokenType,
        Long expiresInSeconds,
        UserResponse user
) {}
