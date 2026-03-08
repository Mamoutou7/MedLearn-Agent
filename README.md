# MedLearn Agent

MedLearn Agent is a modular AI health education assistant built with **FastAPI**, **LangGraph**, **OpenAI**, and **Tavily**.

It helps users explore health topics, receive plain-language explanations, and optionally complete a short quiz to reinforce understanding.

## What it does

- answers health-related educational questions
- validates whether a query is in scope
- uses web search when the model needs external information
- offers a resumable quiz flow with approval and answer steps
- exposes the workflow through a clean FastAPI API
- includes basic logging, tracing, and in-process metrics

## Core workflow

1. Create a session
2. Send a health question
3. Validate that the topic is health-related
4. Generate an explanation
5. Offer a quiz
6. Resume the workflow with quiz approval or rejection
7. If approved, collect the answer and return graded feedback

## Architecture at a glance

The codebase is organized into clear layers:

- `api/` — FastAPI app, routes, schemas, middleware
- `core/` — configuration, logging, exceptions
- `domain/` — shared workflow and quiz models
- `infra/` — LLM and web-search integrations
- `services/` — validation, quiz, explanation, and session logic
- `workflow/` — LangGraph nodes, router, and graph builder
- `observability/` — metrics and tracing helpers
- `repositories/` — persistence boundary for future storage backends
- `prompts/` — prompt templates and prompt management

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

## Testing

```bash
pytest
```

For reliable local setup, make sure all runtime dependencies required by LangChain and LangGraph are installed before running the tests.

## Current limitations

- session state is stored in memory
- prompts are embedded directly in services and workflow nodes
- observability is local and lightweight
- medical safety, source quality, and answer grounding can be strengthened
- there is no persistent checkpointing for long-running sessions

## Roadmap direction

Futures steps:

- move prompts to `src/healthbot/prompts`
- add persistent state and checkpoint storage
- introduce stronger medical safety guardrails
- improve evaluation, reliability, and deployment readiness

## License

Add the appropriate open-source license for public distribution.
