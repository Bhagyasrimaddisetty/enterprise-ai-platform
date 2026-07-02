from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.config import get_settings
from app.core.security import CurrentUser, get_current_user
from app.schemas.schemas import (
    DocumentIngestResponse,
    InterviewAnswerEvaluationRequest,
    InterviewAnswerEvaluationResponse,
    InterviewQuestionRequest,
    InterviewQuestionResponse,
    RagQueryRequest,
    RagQueryResponse,
    ResumeAnalysisRequest,
    ResumeAnalysisResponse,
)
from app.services.interview_service import InterviewService
from app.services.rag_service import RagService
from app.services.resume_analyzer import ResumeAnalyzer
from app.services.vector_store import DocumentStore

router = APIRouter()

_analyzer = ResumeAnalyzer()
_store = DocumentStore()
_rag = RagService(store=_store)
_interview = InterviewService(resume_analyzer=_analyzer)


@router.post("/resume/analyze", response_model=ResumeAnalysisResponse, tags=["Resume Analyzer"])
def analyze_resume(payload: ResumeAnalysisRequest, user: CurrentUser = Depends(get_current_user)):
    return _analyzer.analyze(payload.resume_text, payload.job_description)


@router.post("/documents/ingest", response_model=DocumentIngestResponse, tags=["Document RAG"])
async def ingest_document(file: UploadFile = File(...), user: CurrentUser = Depends(get_current_user)):
    settings = get_settings()
    contents = await file.read()
    if len(contents) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_mb}MB limit")

    if file.filename.lower().endswith(".pdf"):
        text = _store.extract_pdf_text(contents)
    else:
        text = contents.decode("utf-8", errors="ignore")

    if not text.strip():
        raise HTTPException(status_code=422, detail="No extractable text found in document")

    document_id, chunk_count = _store.ingest(text, file.filename)
    return DocumentIngestResponse(document_id=document_id, filename=file.filename, chunk_count=chunk_count)


@router.post("/documents/query", response_model=RagQueryResponse, tags=["Document RAG"])
async def query_document(payload: RagQueryRequest, user: CurrentUser = Depends(get_current_user)):
    if not _store.document_exists(payload.document_id):
        raise HTTPException(status_code=404, detail="document_id not found")
    return await _rag.answer(payload.document_id, payload.question, payload.top_k)


@router.post("/interview/questions", response_model=InterviewQuestionResponse, tags=["Interview"])
async def generate_interview_questions(payload: InterviewQuestionRequest, user: CurrentUser = Depends(get_current_user)):
    questions, generated_by = await _interview.generate_questions(
        payload.resume_text, payload.job_description, payload.experience_level,
        payload.question_types, payload.count_per_type,
    )
    return InterviewQuestionResponse(questions=questions, generated_by=generated_by)


@router.post("/interview/evaluate", response_model=InterviewAnswerEvaluationResponse, tags=["Interview"])
def evaluate_interview_answer(payload: InterviewAnswerEvaluationRequest, user: CurrentUser = Depends(get_current_user)):
    return _interview.evaluate_answer(payload.question, payload.answer_text)
