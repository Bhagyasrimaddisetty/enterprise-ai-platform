package com.platform.resume.dto;

import jakarta.validation.constraints.NotBlank;

public record ResumeUploadRequest(
        @NotBlank String fileName,
        @NotBlank String resumeText,
        String jobDescription
) {}
