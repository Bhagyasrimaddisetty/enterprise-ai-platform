package com.platform.resume.service;

import com.platform.resume.client.AiServiceClient;
import com.platform.resume.dto.AiAnalysisResult;
import com.platform.resume.dto.ResumeUploadRequest;
import com.platform.resume.exception.AiServiceUnavailableException;
import com.platform.resume.exception.ResumeNotFoundException;
import com.platform.resume.model.Resume;
import com.platform.resume.model.ResumeStatus;
import com.platform.resume.repository.ResumeRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestClientException;

import java.time.Instant;
import java.util.List;

@Service
public class ResumeService {

    private final ResumeRepository resumeRepository;
    private final AiServiceClient aiServiceClient;

    public ResumeService(ResumeRepository resumeRepository, AiServiceClient aiServiceClient) {
        this.resumeRepository = resumeRepository;
        this.aiServiceClient = aiServiceClient;
    }

    @Transactional
    public Resume upload(String ownerEmail, ResumeUploadRequest request) {
        Resume resume = Resume.builder()
                .ownerEmail(ownerEmail)
                .fileName(request.fileName())
                .extractedText(request.resumeText())
                .jobDescription(request.jobDescription())
                .status(ResumeStatus.UPLOADED)
                .build();
        return resumeRepository.save(resume);
    }

    @Transactional
    public Resume analyze(Long resumeId, String ownerEmail, String bearerToken) {
        Resume resume = getOwnedResume(resumeId, ownerEmail);

        if (resume.getJobDescription() == null || resume.getJobDescription().isBlank()) {
            throw new IllegalStateException("Resume has no job description attached — cannot compute ATS score");
        }

        try {
            AiAnalysisResult result = aiServiceClient.analyzeResume(
                    resume.getExtractedText(), resume.getJobDescription(), bearerToken);

            resume.setAtsScore(result.atsScore());
            resume.setKeywordMatchScore(result.keywordMatchScore());
            resume.setSemanticSimilarityScore(result.semanticSimilarityScore());
            resume.setMatchedSkillsCsv(String.join(",", result.skills().matchedSkills()));
            resume.setMissingSkillsCsv(String.join(",", result.skills().missingSkills()));
            resume.setStatus(ResumeStatus.ANALYZED);
            resume.setAnalyzedAt(Instant.now());
        } catch (RestClientException e) {
            resume.setStatus(ResumeStatus.FAILED);
            resumeRepository.save(resume);
            throw new AiServiceUnavailableException("Could not reach ai-service for analysis", e);
        }

        return resumeRepository.save(resume);
    }

    public List<Resume> listForOwner(String ownerEmail) {
        return resumeRepository.findByOwnerEmailOrderByCreatedAtDesc(ownerEmail);
    }

    public Resume getOwnedResume(Long id, String ownerEmail) {
        Resume resume = resumeRepository.findById(id).orElseThrow(() -> new ResumeNotFoundException(id));
        if (!resume.getOwnerEmail().equals(ownerEmail)) {
            throw new ResumeNotFoundException(id); // don't leak existence to non-owners
        }
        return resume;
    }

    @Transactional
    public void delete(Long id, String ownerEmail) {
        Resume resume = getOwnedResume(id, ownerEmail);
        resumeRepository.delete(resume);
    }
}
