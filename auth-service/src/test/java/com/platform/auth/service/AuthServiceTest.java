package com.platform.auth.service;

import com.platform.auth.config.JwtProperties;
import com.platform.auth.dto.AuthResponse;
import com.platform.auth.dto.LoginRequest;
import com.platform.auth.dto.RegisterRequest;
import com.platform.auth.exception.EmailAlreadyExistsException;
import com.platform.auth.exception.InvalidCredentialsException;
import com.platform.auth.model.Role;
import com.platform.auth.model.User;
import com.platform.auth.repository.UserRepository;
import com.platform.auth.security.JwtUtil;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock
    private UserRepository userRepository;

    private PasswordEncoder passwordEncoder;
    private JwtUtil jwtUtil;
    private AuthService authService;

    @BeforeEach
    void setUp() {
        passwordEncoder = new BCryptPasswordEncoder();
        jwtUtil = new JwtUtil(new JwtProperties("test-secret-for-unit-tests-only-256bit", 3600));
        authService = new AuthService(userRepository, passwordEncoder, jwtUtil);
    }

    @Test
    void register_createsUserAndReturnsToken_whenEmailNotTaken() {
        RegisterRequest request = new RegisterRequest("sri@example.com", "Bhagya Sri", "password123", Role.CANDIDATE);
        when(userRepository.existsByEmail("sri@example.com")).thenReturn(false);
        when(userRepository.save(any(User.class))).thenAnswer(invocation -> {
            User u = invocation.getArgument(0);
            u.setId(1L);
            return u;
        });

        AuthResponse response = authService.register(request);

        assertThat(response.token()).isNotBlank();
        assertThat(response.user().email()).isEqualTo("sri@example.com");
        assertThat(response.user().role()).isEqualTo(Role.CANDIDATE);
    }

    @Test
    void register_throwsEmailAlreadyExists_whenEmailTaken() {
        RegisterRequest request = new RegisterRequest("sri@example.com", "Bhagya Sri", "password123", Role.CANDIDATE);
        when(userRepository.existsByEmail("sri@example.com")).thenReturn(true);

        assertThatThrownBy(() -> authService.register(request))
                .isInstanceOf(EmailAlreadyExistsException.class);
    }

    @Test
    void login_returnsToken_whenCredentialsValid() {
        String rawPassword = "password123";
        User existingUser = User.builder()
                .id(1L).email("sri@example.com").fullName("Bhagya Sri")
                .passwordHash(passwordEncoder.encode(rawPassword))
                .role(Role.CANDIDATE).enabled(true).build();

        when(userRepository.findByEmail("sri@example.com")).thenReturn(Optional.of(existingUser));

        AuthResponse response = authService.login(new LoginRequest("sri@example.com", rawPassword));

        assertThat(response.token()).isNotBlank();
        assertThat(jwtUtil.extractEmail(response.token())).isEqualTo("sri@example.com");
    }

    @Test
    void login_throwsInvalidCredentials_whenPasswordWrong() {
        User existingUser = User.builder()
                .id(1L).email("sri@example.com").fullName("Bhagya Sri")
                .passwordHash(passwordEncoder.encode("correct-password"))
                .role(Role.CANDIDATE).enabled(true).build();

        when(userRepository.findByEmail("sri@example.com")).thenReturn(Optional.of(existingUser));

        assertThatThrownBy(() -> authService.login(new LoginRequest("sri@example.com", "wrong-password")))
                .isInstanceOf(InvalidCredentialsException.class);
    }

    @Test
    void login_throwsInvalidCredentials_whenUserNotFound() {
        when(userRepository.findByEmail("ghost@example.com")).thenReturn(Optional.empty());

        assertThatThrownBy(() -> authService.login(new LoginRequest("ghost@example.com", "anything")))
                .isInstanceOf(InvalidCredentialsException.class);
    }

    @Test
    void login_throwsInvalidCredentials_whenUserDisabled() {
        User disabledUser = User.builder()
                .id(1L).email("sri@example.com").fullName("Bhagya Sri")
                .passwordHash(passwordEncoder.encode("password123"))
                .role(Role.CANDIDATE).enabled(false).build();

        when(userRepository.findByEmail("sri@example.com")).thenReturn(Optional.of(disabledUser));

        assertThatThrownBy(() -> authService.login(new LoginRequest("sri@example.com", "password123")))
                .isInstanceOf(InvalidCredentialsException.class);
    }
}
