package com.platform.gateway.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.reactive.CorsWebFilter;
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource;

import java.util.List;

@Configuration
public class CorsConfig {

    @Bean
    public CorsWebFilter corsWebFilter() {

        CorsConfiguration corsConfig = new CorsConfiguration();

        // Allow only your React frontend
        corsConfig.setAllowedOrigins(List.of("http://localhost:5173"));

        // Allow credentials (JWT/Cookies)
        corsConfig.setAllowCredentials(true);

        // Allowed HTTP methods
        corsConfig.setAllowedMethods(List.of(
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "OPTIONS"
        ));

        // Allow all request headers
        corsConfig.setAllowedHeaders(List.of("*"));

        // Cache preflight response
        corsConfig.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", corsConfig);

        return new CorsWebFilter(source);
    }
}
