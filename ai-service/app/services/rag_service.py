from app.schemas.schemas import RagQueryResponse
from app.services.llm_client import LLMClient, LLMUnavailableError
from app.services.vector_store import DocumentStore


class RagService:
    def __init__(self, store: DocumentStore | None = None, llm: LLMClient | None = None):
        self.store = store or DocumentStore()
        self.llm = llm or LLMClient()

    async def answer(self, document_id: str, question: str, top_k: int = 4) -> RagQueryResponse:
        chunks = self.store.query(document_id, question, top_k)

        if not chunks:
            return RagQueryResponse(
                question=question,
                answer="No relevant content found in this document for that question.",
                sources=[],
                llm_generated=False,
            )

        if self.llm.is_available:
            context = "\n\n".join(f"[{i+1}] {c.text}" for i, c in enumerate(chunks))
            prompt = (
                "Answer the question using ONLY the context below. If the context "
                "doesn't contain the answer, say so explicitly.\n\n"
                f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
            )
            try:
                answer_text = await self.llm.generate(prompt)
                return RagQueryResponse(question=question, answer=answer_text.strip(), sources=chunks, llm_generated=True)
            except LLMUnavailableError:
                pass  # fall through to extractive

        # Extractive fallback — no LLM configured or call failed: return the
        # single best-matching chunk verbatim, clearly labeled as such.
        best = chunks[0]
        return RagQueryResponse(
            question=question,
            answer=f"(Extractive match — no LLM configured) {best.text}",
            sources=chunks,
            llm_generated=False,
        )
