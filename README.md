# MedLearn Agent

AI-powered health education agent built with **LangGraph**, **FastAPI**, **OpenAI**, and **Tavily**.

MedLearn Agent helps users learn about health topics through conversational explanations, optional web-assisted research, and interactive quizzes. The project is structured as a modular, production-oriented AI service with clean separation between API, workflow orchestration, domain models, infrastructure, and observability.

## Highlights

- **Health-focused conversational agent** powered by LangGraph
- **FastAPI service layer** for real API consumption
- **Interactive quiz workflow** with human-in-the-loop interruptions
- **Session-aware agent execution**
- **Structured logging, tracing, and metrics**
- **Clean architecture** with clear module boundaries
- **Unit-test friendly design**

---

## Project Goals

MedLearn Agent is designed to evolve from a prototype notebook-style agent into a **real production-ready AI application**.

The project emphasizes:

- modularity
- maintainability
- observability
- API-first integration
- extensibility toward RAG, multi-agents, and persistent memory

---

## Architecture Overview

The system is organized into dedicated layers:

- **`api/`**: FastAPI application, routes, schemas, middleware, dependency injection
- **`core/`**: settings, exceptions, logging
- **`domain/`**: state and structured models
- **`infra/`**: LLM provider and external tools
- **`services/`**: business logic for validation, quiz generation, explanation, and sessions
- **`workflow/`**: LangGraph nodes, routers, workflow builder
- **`observability/`**: tracing and in-process metrics
- **`utils/`**: helper functions and graph visualization

---

## Detailed Project Structure

```text
MedLearn-Agent/
├── .env
├── .gitignore
├── README.md
├── healthbot_graph.png
├── pytest.ini
├── requirements.txt
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docs/
│   └── architecture.md
│
├── logs/
│   └── healthbot.log
│
├── scripts/
│   └── run_healthbot.py
│
├── src/
│   ├── __init__.py
│   └── healthbot/
│       ├── api/
│       │   ├── app.py
│       │   ├── dependencies.py
│       │   ├── middleware/
│       │   │   ├── error_handler.py
│       │   │   └── request_logging.py
│       │   ├── routes/
│       │   │   ├── chat.py
│       │   │   ├── health.py
│       │   │   └── quiz.py
│       │   └── schemas/
│       │       ├── chat_schema.py
│       │       └── quiz_schema.py
│       ├── cli/
│       │   └── main.py
│       ├── core/
│       │   ├── exceptions.py
│       │   ├── logging.py
│       │   └── settings.py
│       ├── domain/
│       │   ├── models.py
│       │   └── quiz_models.py
│       ├── infra/
│       │   ├── llm_provider.py
│       │   └── web_search_tool.py
│       ├── observability/
│       │   ├── metrics.py
│       │   └── tracing.py
│       ├── prompts/
│       ├── services/
│       │   ├── explanation_service.py
│       │   ├── health_validator.py
│       │   ├── quiz_service.py
│       │   └── session_service.py
│       ├── utils/
│       │   ├── get_interrupt_value.py
│       │   └── visualize_graph.py
│       └── workflow/
│           ├── nodes.py
│           ├── router.py
│           └── workflow_builder.py
│
└── tests/
    ├── test_quiz.py
    ├── test_quiz_approval.py
    ├── test_quiz_grading.py
    ├── test_quiz_service.py
    ├── test_validation.py
    └── test_workflow.py
```

---

## Tech Stack

- Python 3.11+
- FastAPI
- LangGraph
- LangChain
- OpenAI Chat Models
- Tavily Search API
- Pydantic / Pydantic Settings
- Pytest

---

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd MedLearn-Agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file at the root of the project.

Example:

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

---

## Running the Project

### Run the FastAPI server

```bash
uvicorn src.healthbot.api.app:app --host 0.0.0.0 --port 8000 --reload
```

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

### Run the CLI entrypoint

```bash
python scripts/run_healthbot.py
```

---

## API Endpoints

### Create a session

```http
POST /api/v1/sessions
```

### Ask a question

```http
POST /api/v1/chat
Content-Type: application/json

{
  "session_id": "your-session-id",
  "question": "Tell me about malaria"
}
```

### Submit quiz approval

```http
POST /api/v1/quiz/approval
Content-Type: application/json

{
  "session_id": "your-session-id",
  "approved": true
}
```

### Submit quiz answer

```http
POST /api/v1/quiz/answer
Content-Type: application/json

{
  "session_id": "your-session-id",
  "answer": "B"
}
```

### Health and readiness

```http
GET /api/v1/health
GET /api/v1/ready
GET /api/v1/metrics
```

---

## Example Request Flow

1. Create a new session
2. Send a health-related question
3. Receive a summary or an interruption requesting quiz approval
4. Approve or reject the quiz
5. If approved, answer the quiz
6. Receive grading and explanation

This flow mirrors the LangGraph state machine while exposing a clean HTTP API.

---

## Observability

The project includes a lightweight observability layer.

### Logging

- centralized logger configuration in `core/logging.py`
- request logging middleware for API calls
- service-level logs for validation, quiz generation, grading, and LLM initialization

### Tracing

- span-style execution tracing via `observability/tracing.py`
- duration tracking for important operations
- request correlation support

### Metrics

- in-process counters and timing aggregates via `observability/metrics.py`
- basic metrics exposed through `/api/v1/metrics`

---

## Testing

Run the test suite with:

```bash
pytest
```

The existing tests cover:

- validation logic
- quiz generation and grading
- workflow construction and execution

Recommended next additions:

- FastAPI route tests
- middleware tests
- session service tests
- failure-path tests for external tools

---

## Error Handling

The application defines explicit custom exceptions in `core/exceptions.py` and normalizes them through API exception handlers.

This makes failures:

- easier to debug
- safer to expose through HTTP APIs
- more maintainable across the service layer

---

## Production Readiness Status

Already integrated:

- modular architecture
- FastAPI service layer
- centralized settings
- structured logging
- error handlers
- tracing and metrics
- session-aware workflow wrapper
- CI-ready repository structure

Recommended next production steps:

- Redis or Postgres-backed session persistence
- API key or JWT authentication
- request rate limiting
- streaming responses
- Docker and Compose files
- OpenTelemetry / Prometheus integration
- LangSmith tracing for agent debugging
- background job support for asynchronous workloads

---

## Contribution Guide

### Development principles

- keep modules small and single-purpose
- avoid mixing workflow orchestration with HTTP layer logic
- prefer typed schemas and explicit exceptions
- keep prompts isolated and reusable
- write tests for each service and route addition

### Suggested workflow

1. Create a feature branch
2. Add or update tests
3. Implement the change
4. Run `pytest`
5. Open a pull request

---

## Vision

MedLearn Agent is structured to become more than a demo chatbot.

It is a foundation for:

- production AI health tutoring
- tool-augmented educational agents
- workflow-driven human-in-the-loop systems
- future RAG and multi-agent medical learning platforms

---

## License

Add your preferred license file, such as MIT, Apache-2.0, or a private internal license.
