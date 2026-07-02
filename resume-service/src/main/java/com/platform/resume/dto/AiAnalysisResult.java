package com.platform.resume.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public record AiAnalysisResult(
        double atsScore,
        double keywordMatchScore,
        double semanticSimilarityScore,
        SkillsBlock skills,
        List<String> suggestions
) {
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record SkillsBlock(List<String> matchedSkills, List<String> missingSkills, List<String> extraSkills) {}
}
