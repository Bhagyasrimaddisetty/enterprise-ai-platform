from app.services.resume_analyzer import ResumeAnalyzer

RESUME = """
Bhagya Sri - Software Engineer
Skills: Python, FastAPI, React, PostgreSQL, Docker, Spring Boot, JUnit, Git
Built a resume analyzer using Python and FastAPI with PostgreSQL storage.
Experience with Docker containerization and REST API design.
"""

JD_MATCHING = """
We are looking for a Software Engineer with experience in Python, FastAPI,
PostgreSQL, Docker, and REST API design. Spring Boot experience is a plus.
"""

JD_MISMATCHED = """
We are looking for a Data Engineer with deep expertise in Apache Spark,
Airflow, Kafka, Scala, and Elasticsearch for large scale ETL pipelines.
"""


def test_analyze_returns_valid_score_range():
    analyzer = ResumeAnalyzer()
    result = analyzer.analyze(RESUME, JD_MATCHING)
    assert 0 <= result.ats_score <= 100
    assert 0 <= result.keyword_match_score <= 100
    assert 0 <= result.semantic_similarity_score <= 100


def test_matching_jd_scores_higher_than_mismatched_jd():
    analyzer = ResumeAnalyzer()
    good_match = analyzer.analyze(RESUME, JD_MATCHING)
    bad_match = analyzer.analyze(RESUME, JD_MISMATCHED)
    assert good_match.ats_score > bad_match.ats_score


def test_matched_skills_detected():
    analyzer = ResumeAnalyzer()
    result = analyzer.analyze(RESUME, JD_MATCHING)
    assert "python" in result.skills.matched_skills
    assert "fastapi" in result.skills.matched_skills
    assert "docker" in result.skills.matched_skills


def test_missing_skills_detected_for_mismatched_jd():
    analyzer = ResumeAnalyzer()
    result = analyzer.analyze(RESUME, JD_MISMATCHED)
    assert "kafka" in result.skills.missing_skills or "apache spark" not in result.skills.matched_skills
    assert len(result.skills.missing_skills) > 0


def test_multiword_skill_not_falsely_matched_as_substring():
    analyzer = ResumeAnalyzer()
    # "java" should NOT match inside "javascript"
    text = "Experienced in JavaScript and TypeScript development."
    skills = analyzer._extract_skills(text)
    assert "java" not in skills
    assert "javascript" in skills


def test_empty_jd_skills_gives_zero_keyword_score():
    analyzer = ResumeAnalyzer()
    result = analyzer.analyze(RESUME, "General role, no specific tech mentioned, team player wanted.")
    assert result.keyword_match_score == 0.0


def test_suggestions_are_non_empty():
    analyzer = ResumeAnalyzer()
    result = analyzer.analyze(RESUME, JD_MISMATCHED)
    assert len(result.suggestions) > 0
