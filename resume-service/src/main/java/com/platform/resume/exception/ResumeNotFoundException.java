package com.platform.resume.exception;

public class ResumeNotFoundException extends RuntimeException {
    public ResumeNotFoundException(Long id) {
        super("No resume found with id " + id);
    }
}
