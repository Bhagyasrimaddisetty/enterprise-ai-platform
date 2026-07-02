package com.platform.auth.dto;

import com.platform.auth.model.Role;
import com.platform.auth.model.User;

public record UserResponse(
        Long id,
        String email,
        String fullName,
        Role role
) {
    public static UserResponse from(User user) {
        return new UserResponse(user.getId(), user.getEmail(), user.getFullName(), user.getRole());
    }
}
