"""
Resume Analyzer.

Two independent, real signals are combined into the ATS score:
  1. keyword_match_score  — overlap between skills found in the resume vs
                             skills found in the job description, using a
                             curated skills dictionary (data/skills/skills_dictionary.json).
  2. semantic_similarity   — cosine similarity between TF-IDF vectors of the
                             full resume text and the full JD text. This
                             captures phrasing/context overlap beyond exact
                             keyword hits.

No network call, no LLM required — this runs fully offline and
deterministically, which also makes it trivially unit-testable.
"""
import json
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import get_settings
from app.schemas.schemas import ResumeAnalysisResponse, SkillGap


class ResumeAnalyzer:
    def __init__(self, skills_dict_path: str | None = None):
        settings = get_settings()
        path = Path(skills_dict_path or settings.skills_dict_path)
        with open(path, "r", encoding="utf-8") as f:
            self._skills = [s.lower() for s in json.load(f)["skills"]]

    def _extract_skills(self, text: str) -> set[str]:
        text_lower = text.lower()
        found = set()
        for skill in self._skills:
            # word-boundary match; handles multi-word skills like "spring boot"
            pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
            if re.search(pattern, text_lower):
                found.add(skill)
        return found

    @staticmethod
    def _semantic_similarity(text_a: str, text_b: str) -> float:
        vectorizer = TfidfVectorizer(stop_words="english")
        try:
            matrix = vectorizer.fit_transform([text_a, text_b])
        except ValueError:
            # empty vocabulary after stopword removal (e.g. both texts trivial)
            return 0.0
        score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return round(float(score) * 100, 2)

    def _suggestions(self, missing: set[str], keyword_score: float, semantic_score: float) -> list[str]:
        suggestions = []
        if missing:
            top_missing = sorted(missing)[:6]
            suggestions.append(
                "Add or highlight these JD keywords if you genuinely have the experience: "
                + ", ".join(top_missing)
            )
        if keyword_score < 40:
            suggestions.append(
                "Keyword overlap with the job description is low — mirror the JD's exact "
                "terminology for skills you already have, rather than only synonyms."
            )
        if semantic_score < 30:
            suggestions.append(
                "Overall phrasing overlap with the JD is low — consider rewriting bullet "
                "points to reflect the responsibilities described in the JD more directly."
            )
        if not suggestions:
            suggestions.append("Strong alignment with this job description — no major gaps detected.")
        return suggestions

    def analyze(self, resume_text: str, job_description: str) -> ResumeAnalysisResponse:
        resume_skills = self._extract_skills(resume_text)
        jd_skills = self._extract_skills(job_description)

        matched = resume_skills & jd_skills
        missing = jd_skills - resume_skills
        extra = resume_skills - jd_skills

        keyword_score = round((len(matched) / len(jd_skills) * 100), 2) if jd_skills else 0.0
        semantic_score = self._semantic_similarity(resume_text, job_description)

        # Blended ATS score: keyword overlap weighted higher, since that's
        # what most real ATS keyword scanners key off of; semantic score
        # softens the edge case of a resume that uses different wording
        # for the same underlying skill.
        ats_score = round(keyword_score * 0.65 + semantic_score * 0.35, 2)

        return ResumeAnalysisResponse(
            ats_score=ats_score,
            keyword_match_score=keyword_score,
            semantic_similarity_score=semantic_score,
            skills=SkillGap(
                matched_skills=sorted(matched),
                missing_skills=sorted(missing),
                extra_skills=sorted(extra),
            ),
            suggestions=self._suggestions(missing, keyword_score, semantic_score),
        )
