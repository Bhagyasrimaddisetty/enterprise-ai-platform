import pytest

from app.services.rag_service import RagService
from app.services.vector_store import DocumentStore

DOC_TEXT = """
Leave Policy

Employees are entitled to 18 paid leave days per calendar year. Sick leave
requires a medical certificate if taken for more than two consecutive days.
Unused leave can be carried forward up to a maximum of 10 days into the next
calendar year.

Remote Work Policy

Employees may work remotely up to two days per week with manager approval.
All remote work requires a stable internet connection and availability
during core hours, 10 AM to 4 PM.
"""


@pytest.fixture
def store(tmp_vector_store_dir):
    return DocumentStore(base_dir=tmp_vector_store_dir)


def test_ingest_creates_chunks(store):
    document_id, chunk_count = store.ingest(DOC_TEXT, "policy.txt")
    assert document_id
    assert chunk_count > 0
    assert store.document_exists(document_id)


def test_query_retrieves_relevant_chunk(store):
    document_id, _ = store.ingest(DOC_TEXT, "policy.txt")
    results = store.query(document_id, "How many paid leave days do employees get?", top_k=2)
    assert len(results) > 0
    assert "18" in results[0].text or "leave" in results[0].text.lower()


def test_query_nonexistent_document_raises(store):
    with pytest.raises(FileNotFoundError):
        store.query("does-not-exist", "any question")


def test_ingest_empty_text_raises(store):
    with pytest.raises(ValueError):
        store.ingest("", "empty.txt")


@pytest.mark.asyncio
async def test_rag_service_extractive_fallback_without_llm(store):
    # LLMClient defaults to provider "none" unless env configures otherwise
    service = RagService(store=store)
    document_id, _ = store.ingest(DOC_TEXT, "policy.txt")
    response = await service.answer(document_id, "What is the remote work policy?")
    assert response.llm_generated is False
    assert len(response.sources) > 0
    assert "Extractive" in response.answer or "remote" in response.answer.lower()
