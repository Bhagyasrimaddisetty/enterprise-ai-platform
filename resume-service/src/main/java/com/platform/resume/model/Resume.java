package com.platform.resume.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.Instant;

@Entity
@Table(name = "resumes")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Resume {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String ownerEmail;

    @Column(nullable = false)
    private String fileName;

    @Lob
    @Column(nullable = false)
    private String extractedText;

    @Lob
    private String jobDescription;

    @Enumerated(EnumType.STRING)
    @Builder.Default
    private ResumeStatus status = ResumeStatus.UPLOADED;

    private Double atsScore;
    private Double keywordMatchScore;
    private Double semanticSimilarityScore;

    @Lob
    private String matchedSkillsCsv;

    @Lob
    private String missingSkillsCsv;

    @Column(nullable = false, updatable = false)
    private Instant createdAt;

    private Instant analyzedAt;

    @PrePersist
    void onCreate() {
        this.createdAt = Instant.now();
    }
}
