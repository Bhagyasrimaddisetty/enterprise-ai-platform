package com.platform.resume.dto;

import com.platform.resume.model.Resume;
import com.platform.resume.model.ResumeStatus;

import java.time.Instant;
import java.util.Arrays;
import java.util.List;

public record ResumeResponse(
        Long id,
        String fileName,
        ResumeStatus status,
        Double atsScore,
        Double keywordMatchScore,
        Double semanticSimilarityScore,
        List<String> matchedSkills,
        List<String> missingSkills,
        Instant createdAt,
        Instant analyzedAt
) {
    public static ResumeResponse from(Resume r) {
        return new ResumeResponse(
                r.getId(), r.getFileName(), r.getStatus(),
                r.getAtsScore(), r.getKeywordMatchScore(), r.getSemanticSimilarityScore(),
                toList(r.getMatchedSkillsCsv()), toList(r.getMissingSkillsCsv()),
                r.getCreatedAt(), r.getAnalyzedAt()
        );
    }

    private static List<String> toList(String csv) {
        if (csv == null || csv.isBlank()) return List.of();
        return Arrays.stream(csv.split(",")).map(String::trim).filter(s -> !s.isEmpty()).toList();
    }
}
