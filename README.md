# MedLearn Agent

MedLearn Agent is a modular AI health education assistant built with **FastAPI**, **LangGraph**, **OpenAI**, and **Tavily**.

It helps users explore health topics, receive plain-language explanations, and optionally complete a short quiz to reinforce understanding.

## What it does

- answers health-related educational questions
- validates whether a query is in scope
- uses curated web search when the model needs external information
- offers a resumable quiz flow with approval and answer steps
- persists sessions across restarts with pluggable storage backends
- supports persistent checkpointing for long-running workflows
- centralizes prompts for easier maintenance and versioning
- exposes the workflow through a clean FastAPI API
- includes structured logging, tracing, and lightweight metrics export
- strengthens medical safety, source quality, and answer grounding

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
- `prompts/` — centralized prompt templates and prompt registry

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

```bash
git clone <repo-url>
cd MedLearn-Agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```bash
.venv\Scripts\activate
```

## Environment variables

Create a `.env` file at the project root:

```env
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
MODEL_NAME=gpt-4o-mini

APP_NAME=MedLearn Agent
APP_ENV=development
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
ALLOWED_ORIGINS=*

# Session persistence
SESSION_BACKEND=sqlite
SESSION_SQLITE_PATH=.data/sessions.db
SESSION_BACKEND_FALLBACK_ENABLED=true

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
SESSION_TTL_SECONDS=86400
REDIS_KEY_PREFIX=medlearn

# Workflow checkpointing
CHECKPOINT_BACKEND=sqlite
CHECKPOINT_SQLITE_PATH=.data/langgraph_checkpoints.db
CHECKPOINT_POSTGRES_URL=

# Observability
OBSERVABILITY_BACKEND=prometheus_text

# Source quality / grounding
TRUSTED_HEALTH_DOMAINS=cdc.gov,who.int,nih.gov,medlineplus.gov,nhs.uk,mayoclinic.org,clevelandclinic.org,nice.org.uk,msdmanuals.com
SOURCE_RESULT_LIMIT=5
```

## Run the API

```bash
uvicorn src.healthbot.api.app:app --host 0.0.0.0 --port 8000 --reload
```

Interactive docs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Run the CLI entrypoint

```bash
python scripts/run_healthbot.py
```

## Main API endpoints

- `POST /api/v1/sessions` — create a session
- `GET /api/v1/sessions/{session_id}` — retrieve session history
- `POST /api/v1/chat` — ask a health question
- `POST /api/v1/quiz/approval` — approve or reject the quiz
- `POST /api/v1/quiz/answer` — submit a quiz answer
- `GET /api/v1/health` — liveness probe
- `GET /api/v1/ready` — readiness probe
- `GET /api/v1/metrics` — metrics snapshot
- `GET /api/v1/metrics/prometheus` — Prometheus-style metrics export



## Testing
### Regression and units testing
```bash
pytest
```
### Prompt evaluation

Run the prompt evaluation suite:

```bash
python -m scripts.run_prompt_evals
```

## Current limitations
- observability is still lightweight compared with a full production telemetry stack 
- Redis and Postgres deployment paths may require additional infra wiring depending on environment 
- medical safety is improved (red flag detection, grounding hints) but remains educational and must not be used for clinical decision-making
- prompt evaluation and regression testing are implemented but can be expanded with larger datasets, automated CI gating, and LLM-as-judge approaches
- source retrieval quality depends on external search and prompt behavior 

## Roadmap direction

Futures steps:
- introduce automated regression gating in CI based on evaluation score thresholds
- implement LLM-as-judge evaluation and comparison between prompt versions
- integrate OpenTelemetry + Prometheus + Grafana for production-grade observability
- add distributed tracing across API, workflow, and tool layers
- support advanced prompt versioning (A/B testing, audit logs, rollback mechanisms)
- improve medical safety with structured guardrails (risk classification, escalation policies)
- enhance source grounding with citation formatting and evidence ranking
- add full production-ready deployment paths (Docker Compose, Kubernetes, managed Redis/Postgres)
- strengthen checkpointing with recovery workflows, replay capabilities, and long-session resilience
- introduce rate limiting, authentication, and API governance

## License

Add the appropriate open-source license for public distribution.
