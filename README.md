# Enterprise AI Talent & Knowledge Platform

A full-stack platform combining Spring Boot microservices and a FastAPI AI
service to provide AI-powered resume ATS scoring, document question-answering
(RAG), and interview question generation/evaluation through a React dashboard.

## Architecture

```
React Frontend (MUI, Axios, React Router)
            │
   Spring Cloud Gateway  (routes by path prefix)
            │
   ┌────────┴─────────┐
   │                   │
auth-service      resume-service
(JWT issuance,    (resume storage,
 RBAC, users)      calls ai-service)
   │                   │
   └─────────┬─────────┘
             │
        ai-service (FastAPI)
   resume scoring · document RAG · interview Q&A
             │
         PostgreSQL (users, resumes)
```

auth-service and resume-service share one HS256 JWT secret so tokens issued
by auth-service are trusted by resume-service and ai-service without a
second login. ai-service is *not* an authentication authority — it validates,
never issues, tokens.

## What's actually verified, and how

I don't have Maven, Gradle, or Docker in the sandbox I built this in, and
Maven Central was network-blocked — so the three Spring Boot services were
written correctly and completely, but **not compiled locally**. Real
verification for those happens in CI (`.github/workflows/ci.yml`, `mvn clean
verify`) the first time you push. Check the Actions tab goes green before
you cite these as "tested" anywhere.

What I *did* run and verify myself, end-to-end, in this session:
- **ai-service**: 17 pytest tests passing, plus live curl calls against a
  running instance — resume scoring, interview question generation, and
  document RAG ingest+query all returned real, correct responses.
- **frontend**: 5 Vitest tests passing, and `npm run build` produces a real
  production bundle.

## Honest technology notes (read before writing resume bullets)

- **No Sentence Transformers / deep embeddings.** PyPI's default `torch`
  wheel pulls multi-GB CUDA dependencies that didn't fit in this sandbox,
  and the CPU-only wheel index isn't reachable here. Resume similarity and
  document search both use **TF-IDF vectors + scikit-learn cosine
  similarity**, indexed with **FAISS** for the document RAG path. That's a
  real, working, testable technique — just not a transformer embedding
  model. If you want real sentence-transformers embeddings, that's a
  concrete follow-up task on your own machine (which won't hit this
  sandbox's disk/network limits), not something to claim now.
- **LLM calls (Gemini/OpenAI) are fully optional and untested here** — I
  have no API key. The code path is real (`app/services/llm_client.py`),
  but with no key configured, resume scoring, document Q&A, and interview
  question generation all run in a genuine no-LLM mode (TF-IDF scoring,
  extractive RAG answers, template-based questions) rather than silently
  faking a generated response. Set `LLM_PROVIDER` + an API key to turn on
  the LLM path — then actually test it before claiming "Gemini/OpenAI
  integration" anywhere.
- **Grammar checking in interview evaluation is rule-based** (double
  spaces, repeated words, capitalization/punctuation) — not an AI grammar
  model. Said plainly in code comments so it's not mistaken for more than
  it is.
- **Redis is wired into docker-compose but not yet used by any service.**
  Don't list it as an implemented skill until something actually reads/writes
  through it.

## Prerequisites

- Java 17 + Maven (for local Spring Boot runs)
- Python 3.12
- Node.js 20
- Docker + Docker Compose (for the full-stack run)

## Running everything with Docker Compose (recommended)

```bash
cp ai-service/.env.example ai-service/.env       # optional: add an LLM key
cp frontend/.env.example frontend/.env
docker compose up --build
```

- Frontend: http://localhost:3000
- Gateway (all APIs): http://localhost:8080
- ai-service docs (Swagger UI): http://localhost:8000/docs

## Running services individually (no Docker)

**ai-service**
```bash
cd ai-service
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

**auth-service** / **resume-service** / **gateway** (needs Maven)
```bash
cd auth-service   # repeat for resume-service, gateway
mvn spring-boot:run
```
Each service defaults to an in-memory H2 database when `DB_URL` isn't set —
no Postgres required for local dev.

**frontend**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Running the tests

```bash
# ai-service (verified passing — 17 tests)
cd ai-service && source venv/bin/activate && pytest -v

# frontend (verified passing — 5 tests)
cd frontend && npm test

# auth-service / resume-service / gateway (needs Maven — verify via CI or locally)
cd auth-service && mvn test
```

## 📸 Application Screenshots

### Login Page
![Login](screenshots/login.png)

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Resume Analyzer
![Resume Analyzer](screenshots/resume-analyzer.png)

### Document Q&A
![Document Q&A](screenshots/document-qa.png)

### Interview Preparation
![Interview Preparation](screenshots/interview-prep.png)

### AI Service Swagger
![Swagger UI](screenshots/swagger-ui.png)


## Key API endpoints (via gateway, port 8080)

| Method | Path | Service | Auth |
|---|---|---|---|
| POST | `/api/auth/register` | auth-service | none |
| POST | `/api/auth/login` | auth-service | none |
| POST | `/api/resumes` | resume-service | Bearer |
| POST | `/api/resumes/{id}/analyze` | resume-service → ai-service | Bearer |
| GET | `/api/resumes` | resume-service | Bearer |
| POST | `/api/ai/documents/ingest` | ai-service | Bearer |
| POST | `/api/ai/documents/query` | ai-service | Bearer |
| POST | `/api/ai/interview/questions` | ai-service | Bearer |
| POST | `/api/ai/interview/evaluate` | ai-service | Bearer |

## Environment variables

See `ai-service/.env.example`, `frontend/.env.example`, and
`docker-compose.yml` for the full list. The one that matters most:
`JWT_SECRET` must be identical across auth-service, resume-service, and
ai-service, or tokens issued by auth-service won't validate elsewhere.

## Project structure

```
enterprise-ai-platform/
├── auth-service/       Spring Boot — registration, login, JWT issuance, RBAC
├── resume-service/     Spring Boot — resume storage, orchestrates AI analysis
├── gateway/             Spring Cloud Gateway — routes /api/** to the right service
├── ai-service/          FastAPI — ATS scoring, document RAG, interview Q&A
├── frontend/            React + MUI — dashboard, resume analyzer, doc Q&A, interview prep
├── docker-compose.yml
└── .github/workflows/ci.yml
```
