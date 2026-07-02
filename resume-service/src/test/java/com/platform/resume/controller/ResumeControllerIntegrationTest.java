package com.platform.resume.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.platform.resume.client.AiServiceClient;
import com.platform.resume.dto.AiAnalysisResult;
import com.platform.resume.dto.ResumeUploadRequest;
import com.platform.resume.repository.ResumeRepository;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.List;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class ResumeControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private ResumeRepository resumeRepository;

    @Value("${jwt.secret}")
    private String jwtSecret;

    @MockBean
    private AiServiceClient aiServiceClient;

    @AfterEach
    void cleanUp() {
        resumeRepository.deleteAll();
    }

    private String tokenFor(String email) {
        SecretKey key = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
        return Jwts.builder()
                .subject(email)
                .claim("roles", List.of("CANDIDATE"))
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + 3600_000))
                .signWith(key)
                .compact();
    }

    @Test
    void uploadThenListReturnsResume() throws Exception {
        String token = tokenFor("sri@example.com");
        ResumeUploadRequest request = new ResumeUploadRequest("resume.pdf", "Python FastAPI Docker developer", "Python developer role");

        mockMvc.perform(post("/api/resumes")
                        .header("Authorization", "Bearer " + token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.fileName").value("resume.pdf"))
                .andExpect(jsonPath("$.status").value("UPLOADED"));

        mockMvc.perform(get("/api/resumes").header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].fileName").value("resume.pdf"));
    }

    @Test
    void analyze_returnsAtsScore_whenAiServiceRespondsSuccessfully() throws Exception {
        String token = tokenFor("sri@example.com");
        ResumeUploadRequest request = new ResumeUploadRequest("resume.pdf", "Python FastAPI Docker developer", "Python developer role");

        String uploadJson = mockMvc.perform(post("/api/resumes")
                        .header("Authorization", "Bearer " + token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andReturn().getResponse().getContentAsString();
        Long resumeId = objectMapper.readTree(uploadJson).get("id").asLong();

        when(aiServiceClient.analyzeResume(anyString(), anyString(), anyString())).thenReturn(
                new AiAnalysisResult(88.0, 90.0, 80.0,
                        new AiAnalysisResult.SkillsBlock(List.of("python", "fastapi"), List.of(), List.of()),
                        List.of("Great match"))
        );

        mockMvc.perform(post("/api/resumes/" + resumeId + "/analyze").header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("ANALYZED"))
                .andExpect(jsonPath("$.atsScore").value(88.0));
    }

    @Test
    void accessingAnotherUsersResume_returns404() throws Exception {
        String ownerToken = tokenFor("owner@example.com");
        String intruderToken = tokenFor("intruder@example.com");
        ResumeUploadRequest request = new ResumeUploadRequest("private.pdf", "Confidential resume text", "JD text");

        String uploadJson = mockMvc.perform(post("/api/resumes")
                        .header("Authorization", "Bearer " + ownerToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andReturn().getResponse().getContentAsString();
        Long resumeId = objectMapper.readTree(uploadJson).get("id").asLong();

        mockMvc.perform(get("/api/resumes/" + resumeId).header("Authorization", "Bearer " + intruderToken))
                .andExpect(status().isNotFound());
    }

    @Test
    void upload_withoutToken_returns401() throws Exception {
        ResumeUploadRequest request = new ResumeUploadRequest("resume.pdf", "Some resume text content", null);
        mockMvc.perform(post("/api/resumes")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isUnauthorized());
    }
}
