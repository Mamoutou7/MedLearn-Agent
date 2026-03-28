# MedLearn Agent

MedLearn Agent is a modular AI health education assistant built with **FastAPI**, **LangGraph**, **OpenAI**, and **Tavily**.

It helps users explore health topics, receive plain-language explanations, and optionally complete a short quiz to reinforce understanding.

It is designed to provide safe, structured, and grounded health information while remaining extensible, observable, and production-ready.

## What it does

- answers health-related educational questions
- validates whether a query is in scope
- uses curated web search when the model needs external information
- applies safety guardrails and grounding reinforcement
- offers a resumable quiz flow with approval and answer steps
- persists sessions across restarts with pluggable storage backends
- supports persistent checkpointing for long-running workflows
- centralizes prompts for easier maintenance and versioning
- exposes the workflow through a clean FastAPI API
- includes structured logging, tracing, and metrics export  
- includes prompt evaluation and regression testing  


## Core workflow

1. Create a session
2. Send a health question
3. Validate that the topic is health-related
4. Generate an explanation
5. Optionally retrieve external health evidence from trusted sources
6. Apply safety and grounding reinforcement
7. Offer a quiz
8. Resume the workflow with quiz approval or rejection
9. If approved, collect the answer and return graded feedback

## Architecture at a glance

The codebase is organized into clear layers:

- `api/` — FastAPI app, routes, schemas, middleware  
- `core/` — configuration, logging, exceptions  
- `domain/` — shared workflow and quiz models  
- `infra/` — LLM, web-search, and checkpointing integrations  
- `services/` — validation, quiz, explanation, prompt, safety, and session logic  
- `workflow/` — LangGraph nodes, router, and graph builder  
- `observability/` — metrics and tracing helpers  
- `repositories/` — persistence backends for sessions  
- `prompts/` — centralized prompt templates and registry  
- `evals/` — prompt evaluation and regression datasets  

See [`docs/architecture.md`](docs/architecture.md) for the detailed design.

## Repository structure

```text
MedLearn-Agent/
├── README.md
├── docs/
│   └── architecture.md
├── healthbot_graph.png
├── requirements.txt
├── scripts/
├── src/
│   └── healthbot/
│       ├── api/
│       ├── cli/
│       ├── core/
│       ├── domain/
│       │── evals/
│       ├── infra/
│       ├── observability/
│       ├── prompts/
│       ├── repositories/
│       ├── services/
│       ├── utils/
│       └── workflow/
└── tests/
```

## Tech stack

- Python 3.11+
- FastAPI
- LangGraph / LangChain
- OpenAI chat models
- Tavily Search
- SQLite / Redis for session persistence 
- SQLite / Postgres-ready checkpointing
- Pydantic / pydantic-settings
- Pytest

## Installation

### Clone the repository
```bash
git clone <repo-url>
cd MedLearn-Agent
```
### Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```
### Install dependencies (editable package)
```bash
pip install -e .
```

## Environment variables

Create a `.env` file at the project root:

```env
# LLM
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini

# Search
TAVILY_API_KEY=your_tavily_key

# App
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
API_KEY=your_api_key

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# Session persistence
SESSION_BACKEND=sqlite
SESSION_SQLITE_PATH=.data/sessions.db

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Checkpointing
CHECKPOINT_BACKEND=sqlite
CHECKPOINT_SQLITE_PATH=.data/langgraph_checkpoints.db

# Observability
OBSERVABILITY_BACKEND=prometheus_text

# Grounding / sources
TRUSTED_HEALTH_DOMAINS=cdc.gov,who.int,nih.gov,medlineplus.gov,nhs.uk,mayoclinic.org
SOURCE_RESULT_LIMIT=5
```

## Run the application

### Start API
```bash
uvicorn src.healthbot.api.app:app --host 0.0.0.0 --port 8000 --reload
```

Interactive docs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Run the CLI (human-in-the-loop)

```bash
python -m scripts.run_healthbot
```

## Main API endpoints

- `POST /api/v1/sessions` — create a session
- `GET /api/v1/sessions/{session_id}` — retrieve session history
- `POST /api/v1/chat` — ask a health question
- `POST /api/v1/quiz/approval` — approve or reject the quiz
- `POST /api/v1/quiz/answer` — submit a quiz answer
- `GET /api/v1/health` — liveness probe
- `GET /api/v1/ready` — readiness probe (checks dependencies)
- `GET /api/v1/metrics` — metrics snapshot (protected)
- `GET /api/v1/metrics/prometheus` — Prometheus-style metrics export (protected)


## Security
- API key protection via API_KEY
- Metrics endpoints are protected
- CORS is restricted in production
- LLM calls include retry and timeout safeguards

Prometheus-compatible output is available.


## Observability
Includes:
- structured logging
- request tracing
- metrics (counters, timers, gauges)

## Session persistence
Supported backends:
- memory — development
- sqlite — recommended local persistence
- redis — production

## Checkpointing
Supports resumable workflows:
- SQLite checkpointer (default)
- Postgres-ready interface

Enables:
- recovery after failure
- long-running conversations
- resumable execution

## Medical safety
Includes:
- red flag detection
- educational disclaimers
- grounding hints
- safe refusal of non-health queries

⚠️ This system is not a medical device and must not be used for diagnosis.

## Testing
### Regression and units testing
```bash
pytest
```
Includes: workflow tests, safety regression, prompt regression, and repository tests

### Prompt evaluation & regression testing

```bash
python -m scripts.run_prompt_evals
```
Includes: structured evaluation datasets, scoring (safety, grounding, refusal, keywords), evaluation runner, and regression tests

## Current limitations
- observability is still lightweight compared with a full production telemetry stack 
- Redis and Postgres deployment require environment-specific setup
- medical safety remains educational and not clinical-grade
- source retrieval depends on external APIs and LLM behavior
- prompt evaluation can be expanded (datasets, CI gating, LLM-as-a-judge)
- checkpointing is functional but advanced recovery strategies are still evolving

## Roadmap direction
Futures steps:
- expand evaluation datasets (edge cases, safety-critical scenarios)
- add CI gating based on evaluation scores
- introduce LLM-as-a-judge evaluation
- integrate OpenTelemetry + Prometheus + Grafana
- add distributed tracing
- support prompt versioning and A/B testing
- improve grounding with structured citations
- strengthen medical safety policies
- add production deployment templates (Docker, Kubernetes)
- improve checkpoint recovery and replay capabilities
- introduce rate limiting, authentication, and API governance