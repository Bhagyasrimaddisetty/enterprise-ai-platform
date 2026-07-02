package com.platform.resume;

import com.platform.resume.config.JwtProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@SpringBootApplication
@EnableConfigurationProperties(JwtProperties.class)
public class ResumeServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(ResumeServiceApplication.class, args);
    }
}
