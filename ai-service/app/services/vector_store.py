"""
Document RAG pipeline.

Pipeline: PDF/text -> chunk (LangChain RecursiveCharacterTextSplitter) ->
TF-IDF vectorize chunks (scikit-learn) -> L2-normalize -> index with FAISS
(IndexFlatIP, so inner product on normalized vectors == cosine similarity)
-> persist {index, vectorizer, chunks} per document_id on disk.

Query: vectorize the question with the SAME fitted vectorizer -> FAISS
search -> top-k chunks. If an LLM is configured, those chunks are passed as
context for a grounded answer; otherwise the top chunk(s) are returned
directly as an extractive answer (RagQueryResponse.llm_generated=False makes
this explicit to callers rather than silently pretending to "generate").
"""
import json
import pickle
import uuid
from pathlib import Path

import faiss
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer

from app.core.config import get_settings
from app.schemas.schemas import RetrievedChunk


class DocumentStore:
    def __init__(self, base_dir: str | None = None):
        settings = get_settings()
        self.base_dir = Path(base_dir or settings.vector_store_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800, chunk_overlap=120, separators=["\n\n", "\n", ". ", " "]
        )

    @staticmethod
    def extract_pdf_text(file_bytes: bytes) -> str:
        import io

        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def ingest(self, text: str, filename: str) -> tuple[str, int]:
        chunks = self.splitter.split_text(text)
        if not chunks:
            raise ValueError("Document produced no extractable text/chunks")

        vectorizer = TfidfVectorizer(stop_words="english", max_features=4096)
        matrix = vectorizer.fit_transform(chunks).toarray().astype("float32")
        faiss.normalize_L2(matrix)

        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)

        document_id = str(uuid.uuid4())
        doc_dir = self.base_dir / document_id
        doc_dir.mkdir(parents=True, exist_ok=True)

        faiss.write_index(index, str(doc_dir / "index.faiss"))
        with open(doc_dir / "vectorizer.pkl", "wb") as f:
            pickle.dump(vectorizer, f)
        with open(doc_dir / "chunks.json", "w", encoding="utf-8") as f:
            json.dump({"filename": filename, "chunks": chunks}, f)

        return document_id, len(chunks)

    def query(self, document_id: str, question: str, top_k: int = 4) -> list[RetrievedChunk]:
        doc_dir = self.base_dir / document_id
        if not doc_dir.exists():
            raise FileNotFoundError(f"No such document_id: {document_id}")

        index = faiss.read_index(str(doc_dir / "index.faiss"))
        with open(doc_dir / "vectorizer.pkl", "rb") as f:
            vectorizer: TfidfVectorizer = pickle.load(f)
        with open(doc_dir / "chunks.json", "r", encoding="utf-8") as f:
            chunks = json.load(f)["chunks"]

        q_vec = vectorizer.transform([question]).toarray().astype("float32")
        faiss.normalize_L2(q_vec)

        k = min(top_k, len(chunks))
        scores, indices = index.search(q_vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append(RetrievedChunk(chunk_index=int(idx), text=chunks[idx], score=round(float(score), 4)))
        return results

    def document_exists(self, document_id: str) -> bool:
        return (self.base_dir / document_id).exists()
