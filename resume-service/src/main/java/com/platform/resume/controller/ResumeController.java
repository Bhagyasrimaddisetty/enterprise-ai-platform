package com.platform.resume.controller;

import com.platform.resume.dto.ResumeResponse;
import com.platform.resume.dto.ResumeUploadRequest;
import com.platform.resume.model.Resume;
import com.platform.resume.service.ResumeService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/resumes")
public class ResumeController {

    private final ResumeService resumeService;

    public ResumeController(ResumeService resumeService) {
        this.resumeService = resumeService;
    }

    @PostMapping
    public ResponseEntity<ResumeResponse> upload(@Valid @RequestBody ResumeUploadRequest request,
                                                  Authentication auth) {
        Resume resume = resumeService.upload(auth.getName(), request);
        return ResponseEntity.status(HttpStatus.CREATED).body(ResumeResponse.from(resume));
    }

    @PostMapping("/{id}/analyze")
    public ResponseEntity<ResumeResponse> analyze(@PathVariable Long id,
                                                    Authentication auth,
                                                    @RequestHeader("Authorization") String authHeader) {
        String token = authHeader.replaceFirst("(?i)^Bearer ", "");
        Resume analyzed = resumeService.analyze(id, auth.getName(), token);
        return ResponseEntity.ok(ResumeResponse.from(analyzed));
    }

    @GetMapping
    public ResponseEntity<List<ResumeResponse>> list(Authentication auth) {
        List<ResumeResponse> resumes = resumeService.listForOwner(auth.getName())
                .stream().map(ResumeResponse::from).toList();
        return ResponseEntity.ok(resumes);
    }

    @GetMapping("/{id}")
    public ResponseEntity<ResumeResponse> get(@PathVariable Long id, Authentication auth) {
        Resume resume = resumeService.getOwnedResume(id, auth.getName());
        return ResponseEntity.ok(ResumeResponse.from(resume));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id, Authentication auth) {
        resumeService.delete(id, auth.getName());
        return ResponseEntity.noContent().build();
    }
}
