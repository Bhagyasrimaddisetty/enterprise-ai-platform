from typing import Optional

from pydantic import BaseModel, Field


# ---------- Resume Analyzer ----------

class ResumeAnalysisRequest(BaseModel):
    resume_text: str = Field(..., min_length=20)
    job_description: str = Field(..., min_length=20)


class SkillGap(BaseModel):
    matched_skills: list[str]
    missing_skills: list[str]
    extra_skills: list[str]


class ResumeAnalysisResponse(BaseModel):
    ats_score: float = Field(..., ge=0, le=100)
    keyword_match_score: float = Field(..., ge=0, le=100)
    semantic_similarity_score: float = Field(..., ge=0, le=100)
    skills: SkillGap
    suggestions: list[str]


# ---------- Document RAG ----------

class DocumentIngestResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int


class RagQueryRequest(BaseModel):
    document_id: str
    question: str = Field(..., min_length=3)
    top_k: int = Field(default=4, ge=1, le=10)


class RetrievedChunk(BaseModel):
    chunk_index: int
    text: str
    score: float


class RagQueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[RetrievedChunk]
    llm_generated: bool  # False when llm_provider="none" — answer is extractive, not generated


# ---------- Interview ----------

class InterviewQuestionRequest(BaseModel):
    resume_text: str = Field(..., min_length=20)
    job_description: str = Field(..., min_length=20)
    experience_level: str = Field(default="fresher")  # fresher | mid | senior
    question_types: list[str] = Field(default_factory=lambda: ["technical", "hr", "behavioral"])
    count_per_type: int = Field(default=3, ge=1, le=10)


class InterviewQuestion(BaseModel):
    question_type: str
    question: str


class InterviewQuestionResponse(BaseModel):
    questions: list[InterviewQuestion]
    generated_by: str  # "template_engine" or "llm"


class InterviewAnswerEvaluationRequest(BaseModel):
    question: str
    answer_text: str = Field(..., min_length=1)


class InterviewAnswerEvaluationResponse(BaseModel):
    technical_relevance_score: float = Field(..., ge=0, le=100)
    clarity_score: float = Field(..., ge=0, le=100)
    grammar_issues: list[str]
    overall_score: float = Field(..., ge=0, le=100)
    feedback: str
