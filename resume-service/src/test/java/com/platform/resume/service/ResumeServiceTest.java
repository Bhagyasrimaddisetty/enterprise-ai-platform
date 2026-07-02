package com.platform.resume.service;

import com.platform.resume.client.AiServiceClient;
import com.platform.resume.dto.AiAnalysisResult;
import com.platform.resume.dto.ResumeUploadRequest;
import com.platform.resume.exception.AiServiceUnavailableException;
import com.platform.resume.exception.ResumeNotFoundException;
import com.platform.resume.model.Resume;
import com.platform.resume.model.ResumeStatus;
import com.platform.resume.repository.ResumeRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.web.client.RestClientException;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ResumeServiceTest {

    @Mock
    private ResumeRepository resumeRepository;

    @Mock
    private AiServiceClient aiServiceClient;

    @InjectMocks
    private ResumeService resumeService;

    @BeforeEach
    void setUp() {
        lenient().when(resumeRepository.save(any(Resume.class))).thenAnswer(inv -> {
            Resume r = inv.getArgument(0);
            if (r.getId() == null) r.setId(1L);
            return r;
        });
    }

    @Test
    void upload_savesResumeWithUploadedStatus() {
        ResumeUploadRequest request = new ResumeUploadRequest("resume.pdf", "Python developer with 3 years experience", "Looking for Python dev");

        Resume saved = resumeService.upload("sri@example.com", request);

        assertThat(saved.getStatus()).isEqualTo(ResumeStatus.UPLOADED);
        assertThat(saved.getOwnerEmail()).isEqualTo("sri@example.com");
        verify(resumeRepository).save(any(Resume.class));
    }

    @Test
    void analyze_updatesResumeWithAiScores_onSuccess() {
        Resume resume = Resume.builder()
                .id(1L).ownerEmail("sri@example.com").fileName("r.pdf")
                .extractedText("Python FastAPI Docker").jobDescription("Python developer needed")
                .status(ResumeStatus.UPLOADED).build();
        when(resumeRepository.findById(1L)).thenReturn(Optional.of(resume));

        AiAnalysisResult aiResult = new AiAnalysisResult(
                82.5, 90.0, 70.0,
                new AiAnalysisResult.SkillsBlock(List.of("python"), List.of(), List.of()),
                List.of("Strong match")
        );
        when(aiServiceClient.analyzeResume(anyString(), anyString(), anyString())).thenReturn(aiResult);

        Resume result = resumeService.analyze(1L, "sri@example.com", "fake-token");

        assertThat(result.getStatus()).isEqualTo(ResumeStatus.ANALYZED);
        assertThat(result.getAtsScore()).isEqualTo(82.5);
        assertThat(result.getMatchedSkillsCsv()).isEqualTo("python");
    }

    @Test
    void analyze_marksFailed_whenAiServiceUnreachable() {
        Resume resume = Resume.builder()
                .id(1L).ownerEmail("sri@example.com").fileName("r.pdf")
                .extractedText("Python").jobDescription("Python developer needed")
                .status(ResumeStatus.UPLOADED).build();
        when(resumeRepository.findById(1L)).thenReturn(Optional.of(resume));
        when(aiServiceClient.analyzeResume(anyString(), anyString(), anyString()))
                .thenThrow(new RestClientException("connection refused"));

        assertThatThrownBy(() -> resumeService.analyze(1L, "sri@example.com", "fake-token"))
                .isInstanceOf(AiServiceUnavailableException.class);

        assertThat(resume.getStatus()).isEqualTo(ResumeStatus.FAILED);
    }

    @Test
    void analyze_throwsIllegalState_whenNoJobDescription() {
        Resume resume = Resume.builder()
                .id(1L).ownerEmail("sri@example.com").fileName("r.pdf")
                .extractedText("Python").jobDescription(null)
                .status(ResumeStatus.UPLOADED).build();
        when(resumeRepository.findById(1L)).thenReturn(Optional.of(resume));

        assertThatThrownBy(() -> resumeService.analyze(1L, "sri@example.com", "fake-token"))
                .isInstanceOf(IllegalStateException.class);
    }

    @Test
    void getOwnedResume_throwsNotFound_whenDifferentOwner() {
        Resume resume = Resume.builder().id(1L).ownerEmail("owner@example.com").fileName("r.pdf")
                .extractedText("x").status(ResumeStatus.UPLOADED).build();
        when(resumeRepository.findById(1L)).thenReturn(Optional.of(resume));

        assertThatThrownBy(() -> resumeService.getOwnedResume(1L, "intruder@example.com"))
                .isInstanceOf(ResumeNotFoundException.class);
    }

    @Test
    void getOwnedResume_throwsNotFound_whenIdMissing() {
        when(resumeRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> resumeService.getOwnedResume(99L, "sri@example.com"))
                .isInstanceOf(ResumeNotFoundException.class);
    }

    @Test
    void listForOwner_returnsRepositoryResults() {
        when(resumeRepository.findByOwnerEmailOrderByCreatedAtDesc("sri@example.com"))
                .thenReturn(List.of(Resume.builder().id(1L).ownerEmail("sri@example.com").fileName("a.pdf").extractedText("x").build()));

        List<Resume> results = resumeService.listForOwner("sri@example.com");

        assertThat(results).hasSize(1);
    }
}
