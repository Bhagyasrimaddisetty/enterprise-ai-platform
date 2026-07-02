package com.platform.resume.repository;

import com.platform.resume.model.Resume;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ResumeRepository extends JpaRepository<Resume, Long> {
    List<Resume> findByOwnerEmailOrderByCreatedAtDesc(String ownerEmail);
}
