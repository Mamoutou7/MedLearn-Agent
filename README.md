# MedLearn Agent


MedLearn Agent is a modular AI health education assistant built with **FastAPI**, **LangGraph**, **OpenAI**, and **Tavily**.

It helps users explore health topics, receive plain-language explanations, and optionally complete a short quiz to reinforce learning.

It is designed to provide safe, structured, observable, and grounded health education while remaining extensible and production-oriented.

## What it does

- answers health-related educational questions
- validates whether a query is in scope
- retrieves trusted health evidence when grounding is needed
- applies medical safety guardrails before and after LLM generation
- detects red-flag situations and can short-circuit unsafe flows
- supports structured evidence and citation formatting
- offers a resumable quiz flow with approval and answer steps
- persists sessions across restarts with pluggable storage backends
- supports persistent checkpointing for long-running workflows
- centralizes prompts through an observable `PromptManager`
- exposes the workflow through a clean FastAPI API
- includes structured logging, tracing, metrics, and OpenTelemetry instrumentation
- supports local OpenTelemetry collection with Grafana Alloy
- includes prompt evaluation, regression testing, and CI quality gates


### Evaluation & Quality

MedLearn Agent includes an evaluation pipeline for measuring AI response quality.

It supports:

- **heuristic scoring** using deterministic rubric checks
- **LLM-as-a-judge evaluation**
- **dedicated judge model configuration**
- **combined scoring** using heuristic + judge scores
- **safety scoring**
- **grounding scoring**
- **refusal scoring**
- CI gating based on evaluation thresholds
- expandable evaluation datasets for edge cases, red flags, safety-critical scenarios, and grounding behavior


## Core workflow
1. Create a session
2. Send a health question
3. Validate that the topic is health-related
4. Retrieve trusted external evidence when applicable
5. Generate a grounded educational answer
6. Apply safety and medical policy reinforcement
7. Add citations when sources are available
8. Offer a quiz
9. Resume the workflow with quiz approval or rejection
10. If approved, collect the answer and return graded feedback


## Architecture at a glance

The codebase is organized into clear layers:

- `api/` — FastAPI app, routes, schemas, middleware
- `core/` — configuration, logging, exceptions
- `domain/` — workflow state, quiz models, evidence models
- `infra/` — LLM, observed LLM wrapper, web search, checkpointing integrations
- `services/` — validation, quiz, explanation, prompt, safety, grounding, citation, and session logic
- `workflow/` — LangGraph nodes, router, and graph builder
- `observability/` — metrics, tracing, OpenTelemetry bootstrap
- `repositories/` — persistence backends for sessions
- `prompts/` — centralized prompt templates and registry
- `evals/` — prompt evaluation, rubric scoring, LLM judge, and datasets

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
├── otel/
│   ├── alloy.config.alloy
│   └── docker-compose.yml
├── src/
│   └── healthbot/
│       ├── api/
│       ├── cli/
│       ├── core/
│       ├── domain/
│       ├── evals/
│       ├── infra/
│       ├── observability/
│       ├── prompts/
│       ├── repositories/
│       ├── services/
│       ├── utils/
│       └── workflow/
│── tests/
│── CHANGELOG.md
│── cliff.toml
│── eval_results.json
└── pyproject.toml
```

## Tech stack

- Python 3.13
- FastAPI
- LangGraph / LangChain
- OpenAI chat models
- Tavily Search
- SQLite / Redis for session persistence 
- SQLite / Postgres-ready checkpointing
- Pydantic / pydantic-settings
- Pytest
- Ruff 
- OpenTelemetry 
- Grafana Alloy local collector

## Installation
```bash
git clone <repo-url>
cd MedLearn-Agent
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Environment variables

Create a `.env` file at the project root:

```env
# LLM
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
JUDGE_MODEL_NAME=gpt-4o-mini

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
SESSION_BACKEND_FALLBACK_ENABLED=true

# Redis optional
REDIS_URL=redis://localhost:6379/0
REDIS_KEY_PREFIX=medlearn
SESSION_TTL_SECONDS=86400

# Checkpointing
CHECKPOINT_BACKEND=sqlite
CHECKPOINT_SQLITE_PATH=.data/langgraph_checkpoints.db
CHECKPOINT_POSTGRES_URL=

# Observability
ENABLE_METRICS=true
ENABLE_TRACING=true
OBSERVABILITY_BACKEND=prometheus_text

# OpenTelemetry
OTEL_ENABLED=true
OTEL_SERVICE_NAME=medlearn-agent
OTEL_ENVIRONMENT=development
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces
OTEL_EXPORTER_OTLP_HEADERS=

# Grounding / sources
TRUSTED_HEALTH_DOMAINS=cdc.gov,who.int,nih.gov,medlineplus.gov,nhs.uk,mayoclinic.org,clevelandclinic.org,nice.org.uk,msdmanuals.com
SOURCE_RESULT_LIMIT=5

# Evaluation
ENABLE_LLM_JUDGE=true
AVG_COMBINED_SCORE_THRESHOLD=0.90
AVG_SAFETY_SCORE_THRESHOLD=0.90
AVG_MIN_REFUSAL_SCORE_THRESHOLD=0.90
AVG_GROUNDING_SCORE_THRESHOLD=0.85
```

## Run the application

### Start API
```bash
uvicorn healthbot.api.app:app --host 0.0.0.0 --port 8000 --reload
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

## Local OpenTelemetry collector

The project can send OpenTelemetry traces to a local Grafana Alloy collector.

Start the collector:
```bash
cd otel
docker compose up -d
```

View collector logs:
```bash
docker logs -f medlearn-alloy
```

Stop the collector:
```bash
cd otel
docker compose down
```

The application should use:
```bash
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces
```

## Observability
The system includes:
- structured application logs 
- local request tracing 
- metrics counters, timers, and gauges 
- OpenTelemetry tracing 
- FastAPI instrumentation 
- HTTPX instrumentation 
- LLM invocation spans 
- prompt rendering spans 
- workflow node spans 
- web-search tool spans

Example trace shape:
```bash
POST /api/v1/chat
└── session.ask
    └── workflow.health_agent
        ├── prompt.render
        └── llm.health_agent
```

Example retrieval trace shape:
```bash
workflow.retrieval
└── tool.web_search
```

## Security
- API key protection via API_KEY
- Metrics endpoints are protected
- CORS is restricted in production
- LLM calls include retry and timeout safeguards
- safe refusal of non-health queries 
- red-flag detection for urgent medical situations 
- post-generation medical policy validation

Prometheus-compatible output is available through the metrics endpoint.

## Session persistence
Supported backends:
- `memory` — development
- `sqlite` — recommended local persistence
- `redis` — production

## Checkpointing
Supports resumable workflows:
- SQLite checkpointer (default)
- Postgres-ready interface

It enables:
- recovery after failure
- long-running conversations
- resumable execution
- future replay/debug workflows

## Medical safety
MedLearn Agent includes a layered safety approach.

### Pre-LLM safety classification
A `SafetyClassifier` can detect obvious high-risk cases before calling the LLM.
Examples:
- chest pain with trouble breathing
- possible stroke symptoms
- vomiting blood
- severe abdominal pain with red flags
- mental health crisis
- harmful medical misinformation

If a critical case is detected, the workflow can short-circuit and return an urgent safety message.

### Post-LLM safety enforcement
A `MedicalPolicy` checks generated answers for unsafe patterns such as:
- definitive diagnosis claims
- medication stopping advice
- dosage escalation
- advice to ignore symptoms

### Safety disclaimer
A `SafetyService` reinforces educational framing and urgent-care guidance when needed.

This system is not a medical device and must not be used for diagnosis, treatment decisions, or emergency medical care.


## Grounding and citations

The project includes structured grounding components.

### Evidence model

External search results are normalized into structured evidence objects:
- `EvidenceSource`
- `EvidencePack`

These support: ranking, trusted-source filtering, auditability, citation formatting, answer composition

### Citation formatting
A `CitationFormatter` can render sources like:
Sources reviewed:
```bash
[1] CDC Diabetes — cdc.gov — https://...
[2] WHO — who.int — https://...
```

### Answer composition

An AnswerComposer prepares final user-facing answers from:
- generated answer content
- retrieved evidence sources
- citations
- educational disclaimer


## Prompt management

Prompts are centralized through:
- prompt specs
- prompt registry
- `PromptManager`

The PromptManager provides:
- centralized prompt rendering
- prompt version observability
- prompt render metrics
- OpenTelemetry `prompt.render` spans

This prepares the project for:
- prompt versioning
- A/B testing
- audit workflows
- prompt regression testing


## Evaluation system
The project includes an evaluation pipeline for AI response quality.
### Scoring types 
- **Heuristic score** → rule-based scoring using keywords, safety, grounding, refusal, and forbidden terms
- **Judge score** → LLM-based qualitative evaluation
- **Combined score** → weighted hybrid score
```bash
combined = 0.6 * heuristic + 0.4 * judge
```
**Metrics tracked**: average heuristic score, average judge score, average combined score, average safety score, average grounding score, minimum refusal score
### CI gating
The CI enforces:
```bash
average_combined_score >= AVG_COMBINED_SCORE_THRESHOLD
average_safety_score >= AVG_SAFETY_SCORE_THRESHOLD
min_refusal_score >= AVG_MIN_REFUSAL_SCORE_THRESHOLD
average_grounding_score >= AVG_GROUNDING_SCORE_THRESHOLD
```

### Run prompt evaluations
```bash
python -m scripts.run_prompt_evals
```

With LLM judge enabled:
```bash
ENABLE_LLM_JUDGE=true python -m scripts.run_prompt_evals
```

The results are saved to:
```bash
eval_results.json
```


## Testing
### Regression, integration and units testing
```bash
ruff check . --fix
ruff format .
pytest -q
python -m scripts.run_prompt_evals
```
The test suite includes: 
- workflow tests 
- quiz tests 
- safety tests 
- medical policy tests 
- prompt rendering tests 
- grounding and citation tests 
- repository tests 
- evaluation runner tests

## Current limitations
- observability is still lightweight compared with a complete production telemetry stack
- Grafana Cloud integration is not fully documented yet
- Redis and Postgres deployment require environment-specific setup
- grounding quality depends on retrieval quality and prompt behavior
- checkpointing is functional but advanced recovery strategies are still evolving
- evaluation datasets should be expanded with more edge cases and safety-critical scenarios
- citation formatting is available, but the full source-to-answer flow should continue to be hardened

## Roadmap direction
Futures steps:
- finalize full retrieval-to-citation answer composition
- integrate Grafana Cloud dashboards
- add distributed tracing across API, workflow, LLM, and tools
- support prompt versioning and A/B testing
- improve medical safety policies and red-flag taxonomy
- add richer evidence ranking and structured citation output
- add production deployment templates (Docker, Kubernetes)
- improve checkpoint recovery and replay capabilities
- expand evaluation datasets by category and severity
- add feature flags for web search, strict safety, quiz, and LLM judge