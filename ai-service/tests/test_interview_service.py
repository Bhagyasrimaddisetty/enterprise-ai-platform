import pytest

from app.services.interview_service import InterviewService
from app.services.resume_analyzer import ResumeAnalyzer

RESUME = "Skills: Python, FastAPI, React, PostgreSQL, Docker."
JD = "Looking for a Python and React developer with PostgreSQL and Docker experience."


@pytest.fixture
def service():
    return InterviewService(resume_analyzer=ResumeAnalyzer())


@pytest.mark.asyncio
async def test_generate_questions_template_engine_by_default(service):
    questions, generated_by = await service.generate_questions(
        RESUME, JD, "fresher", ["technical", "hr"], count_per_type=2
    )
    assert generated_by == "template_engine"
    assert len(questions) == 4
    types = {q.question_type for q in questions}
    assert types == {"technical", "hr"}


@pytest.mark.asyncio
async def test_generated_technical_questions_reference_real_skills(service):
    questions, _ = await service.generate_questions(RESUME, JD, "fresher", ["technical"], count_per_type=3)
    combined = " ".join(q.question for q in questions).lower()
    assert any(skill in combined for skill in ["python", "react", "postgresql", "docker", "fastapi"])


def test_evaluate_answer_relevant_scores_higher_than_irrelevant(service):
    question = "Explain how you used Docker in a project you've built."
    relevant = "I containerized a FastAPI service with Docker, using multi-stage builds to keep the image small."
    irrelevant = "I like hiking on weekends and reading books about history."

    good = service.evaluate_answer(question, relevant)
    bad = service.evaluate_answer(question, irrelevant)
    assert good.technical_relevance_score > bad.technical_relevance_score


def test_evaluate_short_answer_flagged_in_feedback(service):
    result = service.evaluate_answer("Why do you want this role?", "Money.")
    assert result.clarity_score < 100
    assert "short" in result.feedback.lower() or "expand" in result.feedback.lower()


def test_grammar_issue_detection():
    issues = InterviewService._grammar_issues("this  has a a double space and repeated word")
    assert any("Double spaces" in i for i in issues)
    assert any("Repeated word" in i for i in issues)
