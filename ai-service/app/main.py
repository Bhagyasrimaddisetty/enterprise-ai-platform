from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "AI microservice for the Enterprise AI Talent & Knowledge Platform: "
        "resume ATS scoring, document RAG search, and interview question "
        "generation/evaluation."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to the gateway/frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/ai")


@app.get("/health", tags=["Health"])
def health():
    return {"status": "UP", "service": settings.app_name, "llm_provider": settings.llm_provider}
