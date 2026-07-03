"""
Thin, pluggable LLM client.

Deliberately NOT a LangChain LLM wrapper — LangChain is used where it earns
its keep (RecursiveCharacterTextSplitter for chunking), but a direct httpx
call is more transparent for the one or two calls this service makes per
request. Swap LLM_PROVIDER in .env between "gemini" / "openai" / "none".

When provider is "none" (no key configured), `is_available` is False and
callers must degrade gracefully instead of raising a fake successful
response — this is what keeps the resume-analyzer and RAG-search paths
usable and testable without any API key at all.
"""
import httpx

from app.core.config import get_settings


class LLMUnavailableError(Exception):
    pass


class LLMClient:
    def __init__(self):
        self.settings = get_settings()
        print("Provider =", self.settings.llm_provider)
        print("Gemini Key Loaded =", bool(self.settings.gemini_api_key))

    @property
    def is_available(self) -> bool:
        if self.settings.llm_provider == "gemini":
            return bool(self.settings.gemini_api_key)
        if self.settings.llm_provider == "openai":
            return bool(self.settings.openai_api_key)
        return False

    async def generate(self, prompt: str, max_tokens: int = 512) -> str:
        if not self.is_available:
            raise LLMUnavailableError(
                "No LLM provider configured. Set LLM_PROVIDER and the matching "
                "API key in .env to enable generated (vs. extractive) responses."
            )

        if self.settings.llm_provider == "gemini":
            return await self._call_gemini(prompt, max_tokens)
        if self.settings.llm_provider == "openai":
            return await self._call_openai(prompt, max_tokens)
        raise LLMUnavailableError(f"Unknown LLM_PROVIDER: {self.settings.llm_provider}")

    async def _call_gemini(self, prompt: str, max_tokens: int) -> str:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-flash:generateContent?key={self.settings.gemini_api_key}"
        )
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens},
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=body)
            resp.raise_for_status()
            data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _call_openai(self, prompt: str, max_tokens: int) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.settings.openai_api_key}"}
        body = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"]
