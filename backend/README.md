# Matrix Biz Automation System — Backend

AI-driven, multi-tenant "Closed-Loop Matrix Business Automation System" (SaaS MVP).

## Tech Stack

- **Framework:** Python FastAPI (async)
- **LLM Orchestration:** LangChain + LangGraph
- **Task Queue:** Celery + Redis
- **Database:** PostgreSQL + SQLAlchemy
- **Validation:** Pydantic v2

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                       # FastAPI entry point
│   ├── config.py                     # Pydantic Settings (env-based)
│   ├── database.py                   # SQLAlchemy engine + session
│   ├── celery_app.py                 # Celery app config
│   ├── models/
│   │   ├── pydantic_models.py        # Request/response schemas
│   │   └── sqlalchemy_models.py      # ORM models (5 tables)
│   ├── routers/
│   │   └── content.py                # /api/v1/content/* endpoints
│   └── services/
│       └── langchain_service.py      # 2-stage prompt chain
├── tasks.py                          # Celery background tasks
├── run.py                            # Dev server (uvicorn)
├── run_celery.py                     # Celery worker launcher
├── requirements.txt
├── .env                              # Local environment variables
└── .env.example                      # Environment template
```

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis

### Setup

```bash
cd backend
cp .env.example .env
# Edit .env with your credentials
pip install -r requirements.txt
```

### Run

**FastAPI server:**
```bash
python run.py
# or: uvicorn app.main:app --reload
```

**Celery worker (separate terminal):**
```bash
python run_celery.py
# or: celery -A app.celery_app worker -l info -P solo
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/content/generate` | Start async content generation |
| GET | `/api/v1/content/task/{task_id}` | Poll generation result |

**POST /api/v1/content/generate**

```json
{
  "industry": "New energy vehicles",
  "style": "Professional",
  "platforms": ["Douyin", "Xiaohongshu"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "task_id": "uuid-task-id",
    "status": "pending",
    "message": "Content generation task queued successfully."
  }
}
```

## Database Schema

Core tables (auto-created on first startup):

| Table | Purpose |
|-------|---------|
| `tenants` | Multi-tenant orgs |
| `users` | Auth + role management |
| `matrix_accounts` | Social platform accounts |
| `content_packages` | Generated content briefs + results |
| `crm_leads` | Customer leads with AI tags |

## Architecture

See the main project README for the full 3-layer closed-loop architecture.

### Content Generation Pipeline

1. **Client** → `POST /api/v1/content/generate`
2. **FastAPI** persists a `content_packages` row (status=`pending`)
3. **FastAPI** enqueues a Celery task
4. **Celery worker** → Stage 1: LLM generates 3 viral angles
5. **Celery worker** → Stage 2: LLM generates platform-specific posts
6. **Celery worker** persists result (status=`completed`)
7. **Client** polls `GET /api/v1/content/task/{task_id}`

Structured output is enforced via LangChain's `with_structured_output` (Pydantic schemas) with a fallback parser that strips Markdown code fences if the LLM wraps JSON in triple backticks.
