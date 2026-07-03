# 🚀 Enterprise AI Talent & Knowledge Platform

![Java](https://img.shields.io/badge/Java-17-orange)
![Spring Boot](https://img.shields.io/badge/SpringBoot-3.x-brightgreen)
![React](https://img.shields.io/badge/React-19-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Python-green)
![JWT](https://img.shields.io/badge/Auth-JWT-red)

A full-stack platform combining Spring Boot microservices and a FastAPI AI
service to provide AI-powered resume ATS scoring, document question-answering
(RAG), and interview question generation/evaluation through a React dashboard.

## ✨ Features

- 🔐 JWT Authentication & Role-Based Access Control
- 📄 AI-powered Resume ATS Analysis
- 📊 Keyword Match & Semantic Similarity Scoring
- 📚 Document Question Answering (RAG)
- 🤖 AI Interview Question Generation
- 📝 Interview Answer Evaluation
- 🌐 Spring Cloud Gateway
- 🏗️ Microservices Architecture

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

## 🛠️ Tech Stack

### Frontend
- React
- Material UI
- Axios
- React Router

### Backend
- Spring Boot
- Spring Security
- Spring Cloud Gateway
- JWT Authentication

### AI Service
- FastAPI
- Scikit-learn
- FAISS
- Gemini API (Optional)

### Database
- PostgreSQL
- H2 (Development)

### Testing
- Pytest
- Vitest

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

## 📸 Application Screenshots

### AI Service Swagger
![Login](Screenshot%202026-07-02%20214114.png)

---

### Dashboard
![Dashboard](Screenshot%202026-07-02%20220911.png)

---

### Login Page
![Resume Analyzer](Screenshot%202026-07-02%20221040.png)
![Document Q&A](Screenshot%202026-07-02%20221046.png)

---

### Interview Preparation
![Interview Preparation](Screenshot%202026-07-03%20131938.png)
![Swagger UI](Screenshot%202026-07-03%20132102.png)

---

### Document Q&A
![Document Q&A](Screenshot%202026-07-03%20141411.png)
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

## 📄 License

This project is licensed under the MIT License.
