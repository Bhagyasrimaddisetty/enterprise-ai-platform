"""
Central configuration for the AI service.

All secrets/keys are read from environment variables (see .env.example).
No key ever has a default value baked into source — if GEMINI_API_KEY or
OPENAI_API_KEY is not set, the service still runs: resume scoring and
document search (TF-IDF + FAISS) work fully offline, and any endpoint that
would need a live LLM call (summarization, interview evaluation narrative,
RAG answer synthesis) returns a clear 503 with an explanation instead of
silently faking a response.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Talent & Knowledge Platform - AI Service"
    environment: str = "development"

    # JWT — must match the secret used by auth-service so tokens issued
    # by Spring Boot are verifiable here too.
    jwt_secret: str = "change-me-in-production-use-256-bit-secret"
    jwt_algorithm: str = "HS256"

    # LLM provider — optional. If unset, LLM-dependent endpoints degrade
    # gracefully rather than pretending to call a model.
    llm_provider: str = "none"  # "gemini" | "openai" | "none"
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Storage
    vector_store_dir: str = "./data/vector_store"
    skills_dict_path: str = "./data/skills/skills_dictionary.json"
    upload_dir: str = "./data/uploads"

    max_upload_mb: int = 15


@lru_cache
def get_settings() -> Settings:
    return Settings()
