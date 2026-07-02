package com.platform.resume.client;

import com.platform.resume.dto.AiAnalysisResult;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.Map;

/**
 * Talks to the FastAPI ai-service. The caller's own bearer token is
 * forwarded so ai-service enforces the same auth/roles rather than
 * resume-service acting as an unauthenticated trusted backend.
 */
@Component
public class AiServiceClient {

    private final RestClient restClient;

    public AiServiceClient(@Value("${ai-service.base-url}") String baseUrl) {
        this.restClient = RestClient.builder().baseUrl(baseUrl).build();
    }

    public AiAnalysisResult analyzeResume(String resumeText, String jobDescription, String bearerToken) {
        return restClient.post()
                .uri("/api/ai/resume/analyze")
                .header("Authorization", "Bearer " + bearerToken)
                .body(Map.of("resume_text", resumeText, "job_description", jobDescription))
                .retrieve()
                .body(AiAnalysisResult.class);
    }
}
