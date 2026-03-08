    # MedLearn Agent Architecture

## Overview

MedLearn Agent is a modular AI health education system designed around a **workflow-oriented agent architecture**.

The application combines:

- **LangGraph** for orchestration
- **FastAPI** for API delivery
- **service-layer abstractions** for business logic
- **observability primitives** for debugging and monitoring
- **clean separation of concerns** to support future production evolution

The architecture is intentionally designed to make the project maintainable, testable, and extensible toward more advanced AI capabilities such as persistent memory, streaming, RAG, and multi-agent collaboration.

---

## Architectural Principles

### 1. Separation of concerns

Each layer has a clearly scoped responsibility:

- API concerns stay in `api/`
- business logic stays in `services/`
- state and structured contracts stay in `domain/`
- infrastructure details stay in `infra/`
- orchestration stays in `workflow/`
- shared runtime concerns stay in `core/`

### 2. Workflow-first design

The core user journey is not modeled as a loose collection of function calls.
It is modeled as a **stateful graph**.

This is essential for agent systems because it supports:

- controlled transitions
- branching logic
- human-in-the-loop interruptions
- resumable execution
- future persistence and checkpointing

### 3. Production-oriented modularity

The codebase is organized so that the same business logic can be exposed through:

- CLI
- HTTP APIs
- future worker processes
- future UI clients

### 4. Observable by design

Production AI systems are difficult to operate without visibility.
The architecture therefore introduces:

- centralized logs
- lightweight tracing spans
- in-process metrics
- HTTP request correlation

---

## High-Level Architecture

```text
Client / CLI / UI
        |
        v
   FastAPI Layer
        |
        v
 Session Service / API Adapters
        |
        v
 LangGraph Workflow
   |        |        |
   v        v        v
Validation  Quiz   Explanation
 Services  Services  Services
        |
        v
 LLM Provider + Tools
        |
        v
 OpenAI / Tavily
```

---

## Detailed Module Responsibilities

## `src/healthbot/api/`

This layer exposes the application through HTTP.

### Responsibilities

- define REST endpoints
- validate payloads with Pydantic schemas
- wire dependencies
- install middleware
- normalize exception handling
- return stable API responses

### Key files

#### `app.py`
Builds the FastAPI application and connects:

- routes
- middleware
- exception handlers
- CORS configuration
- application metadata

#### `dependencies.py`
Provides reusable injected dependencies, such as the session service singleton.

#### `routes/chat.py`
Exposes endpoints to:

- create sessions
- send a user question
- retrieve session history

#### `routes/quiz.py`
Exposes endpoints to:

- approve or reject quiz continuation
- submit quiz answers

#### `routes/health.py`
Exposes operational endpoints:

- liveness
- readiness
- metrics snapshot

#### `middleware/request_logging.py`
Captures request-level telemetry:

- request ID
- method
- path
- status code
- duration

#### `middleware/error_handler.py`
Maps domain and application errors to structured HTTP responses.

---

## `src/healthbot/core/`

This layer contains global runtime building blocks shared across the entire application.

### Responsibilities

- configuration
- logging
- exception definitions
- application-level constants

### Key files

#### `settings.py`
Defines application settings using `pydantic-settings`.

It centralizes configuration such as:

- API host and port
- environment name
- model name
- API keys
- logging level
- CORS origins
- feature toggles

#### `logging.py`
Provides centralized logging configuration.

This ensures every module uses a consistent logging format and output strategy.

#### `exceptions.py`
Defines explicit application exceptions.

Examples include:

- validation errors
- quiz generation errors
- LLM service failures
- workflow errors
- tool execution errors

These custom exceptions help keep failure semantics clear and avoid silent runtime issues.

---

## `src/healthbot/domain/`

This is the domain contract layer.

### Responsibilities

- define shared state models
- define structured quiz contracts
- keep business-facing schemas independent from delivery or infra details

### Key files

#### `models.py`
Contains core workflow state definitions.

#### `quiz_models.py`
Contains Pydantic models used for structured LLM outputs such as:

- quiz questions
- explanations

This layer is intentionally lightweight and stable.

---

## `src/healthbot/infra/`

This layer contains technical integrations with external systems.

### Responsibilities

- instantiate the LLM client
- define tool adapters
- encapsulate external service interaction

### Key files

#### `llm_provider.py`
Owns model initialization.

Benefits:

- central LLM configuration
- easier mocking in tests
- easier future migration between providers

#### `web_search_tool.py`
Wraps Tavily search as a tool usable by the workflow.

This keeps web search logic out of business services and graph nodes.

---

## `src/healthbot/services/`

This is the business logic layer.

It sits between orchestration and infrastructure.

### Responsibilities

- validate user questions
- generate quizzes
- grade answers
- generate explanations
- manage session interactions for the API

### Key files

#### `health_validator.py`
Determines whether a user request is health-related.

It isolates classification logic from the workflow definition.

#### `quiz_service.py`
Contains:

- quiz generation
- quiz approval parsing
- answer validation
- answer grading

#### `explanation_service.py`
Generates detailed educational feedback after grading.

#### `session_service.py`
Acts as the application façade between the HTTP layer and the LangGraph workflow.

It manages:

- session creation
- session state lookup
- workflow invocation
- workflow resume commands
- API-friendly response normalization

This is a critical addition for production readiness because it removes graph handling from route handlers.

---

## `src/healthbot/workflow/`

This is the orchestration layer.

### Responsibilities

- define workflow nodes
- define routing rules
- define graph transitions
- compile the LangGraph workflow

### Key files

#### `nodes.py`
Contains the state transition functions for the workflow.

Examples:

- entry node
- validation node
- agent node
- rejection node
- quiz nodes
- end node

#### `router.py`
Defines conditional routing logic between nodes.

#### `workflow_builder.py`
Builds and compiles the LangGraph graph.

This module is the orchestration backbone of the application.

---

## `src/healthbot/observability/`

This layer provides runtime visibility.

### Responsibilities

- lightweight tracing
- execution metrics
- request correlation

### Key files

#### `tracing.py`
Implements lightweight span tracking around important operations.

This helps identify slow or failing parts of the workflow.

#### `metrics.py`
Stores counters and timing summaries in process.

This is intentionally simple but already useful for:

- debugging
- smoke monitoring
- API inspection

It can later evolve into Prometheus or OpenTelemetry exporters.

---

## `src/healthbot/utils/`

Helper utilities that do not belong directly to a business domain.

### Responsibilities

- interrupt payload handling
- graph visualization support

These helpers remain intentionally small and decoupled.

---

## Workflow Execution Model

The application follows this execution sequence:

1. A client creates or reuses a `session_id`
2. The client sends a health question
3. The API passes the question to `SessionService`
4. `SessionService` invokes the LangGraph workflow
5. The workflow validates the topic
6. If valid, the agent generates an educational response
7. The workflow may interrupt to ask whether a quiz should be generated
8. The client resumes the workflow with approval or rejection
9. If approved, the workflow interrupts again to collect the quiz answer
10. The client resumes the workflow with the answer
11. The workflow grades the answer and returns feedback

This design provides a clean mapping between:

- graph interruptions
- resumable user interactions
- HTTP endpoints

---

## Session Model

The current implementation uses an in-memory session registry through `SessionService`.

### What it supports

- unique `session_id`
- workflow resume by session
- API-level session history

### Why this matters

Agent workflows are stateful. Without sessions, HTTP APIs tend to break the conversational state model.

### Recommended future upgrade

Replace in-memory state with:

- Redis
- Postgres
- LangGraph persistent checkpoint storage

---

## Error Handling Strategy

The application uses layered error handling.

### Service-level errors

Service and infra modules raise explicit exceptions when an operation fails.

### API-level normalization

FastAPI middleware converts application exceptions into structured HTTP responses.

### Benefits

- less duplicated `try/except`
- clearer debugging
- safer external API behavior
- better observability

---

## Observability Strategy

Observability is designed as a cross-cutting concern.

### Logging

Used for:

- application startup
- LLM initialization
- validation decisions
- quiz generation and grading
- tool execution
- HTTP request lifecycle

### Tracing

Used for:

- node-level timing
- service execution spans
- workflow operation timing

### Metrics

Used for:

- request counts
- validation counts
- quiz generation counts
- quiz grading counts
- failure counts
- timing aggregation

This combination is enough for early production environments and can be extended later.

---

## Design Decisions

### Why LangGraph

LangGraph is used because the system is naturally stateful and branching.

It provides:

- explicit transitions
- interrupt/resume behavior
- better agent control than ad-hoc chaining

### Why services separate from workflow

The workflow should orchestrate steps, not implement all business logic inline.

Keeping logic in services improves:

- readability
- testability
- reusability
- maintainability

### Why FastAPI

FastAPI is a strong fit for AI services because it offers:

- async-ready architecture
- Pydantic integration
- automatic OpenAPI docs
- easy integration with modern backends

### Why lightweight observability first

A minimal but connected observability layer is often better than overengineering early with full telemetry stacks.

This project is ready to evolve toward OpenTelemetry, Prometheus, and LangSmith without major refactoring.

---

## Current Production-Ready Capabilities

Already covered:

- modular codebase
- API exposure
- typed request and response models
- centralized config
- centralized logging
- exception normalization
- session-aware workflow adapter
- tracing and metrics hooks
- test-ready layering

---

## Recommended Next Steps

### Short term

- add API route tests with `TestClient`
- add authentication
- add rate limiting
- add persistent session storage
- add Docker and Compose

### Medium term

- add streaming responses
- add Redis-backed caching
- add LangSmith integration
- add OpenTelemetry exporters
- add background task support

### Long term

- add RAG with medical knowledge sources
- add vector storage
- add multi-agent routing
- add policy and safety guardrails
- add model fallback strategies

---

## Conclusion

MedLearn Agent is now structured as a real AI application rather than a single-script prototype.

Its current architecture supports:

- maintainable development
- API-based delivery
- workflow-driven agent execution
- incremental production hardening

This makes it a strong foundation for a serious AI health education platform.
