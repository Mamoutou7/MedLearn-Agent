# MedLearn Agent Architecture

## Overview

MedLearn Agent is a **workflow-driven health education assistant**.

It combines:
- a FastAPI delivery layer
- a LangGraph orchestration engine
- domain-oriented services
- centralized prompt management
- lightweight but structured observability
- evaluation and safety layers

The system is evolving from a strong prototype toward a **production-ready AI backend** with improved reliability, safety, and extensibility.

## Architecture diagram

![MedLearn Agent graph](../healthbot_graph.png)


## Design goals

The architecture aims to be:

- **modular** — clear separation of responsibilities
- **testable** — business logic decoupled from transport and orchestration
- **resumable** — workflow supports interrupt/resume patterns
- **extensible** — prompts, tools, storage, and safety policies are pluggable
- **observable** — metrics, tracing, and evaluation pipelines are integrated
- **reliable** — LLM calls are hardened with retries, timeouts, and fallbacks

## High-level flow

```text
Client / CLI
    |
    v
FastAPI API
    |
    v
SessionService (application façade)
    |
    v
LangGraph workflow
    |
    +--> Health validation
    +--> Health explanation agent
    +--> Optional web search (grounding)
    +--> Safety layer (pre/post processing)
    +--> Quiz approval interrupt
    +--> Quiz generation
    +--> Quiz answer interrupt
    +--> Quiz grading + explanation
```

## Layered architecture

### 1. API layer — `src/healthbot/api`

Responsible for HTTP delivery and external contracts.

**Responsibilities**
- define endpoints
- validate inputs/outputs
- inject dependencies
- expose health, readiness, and metrics endpoints
- enforce API security (API key)
- map internal errors to stable API responses

**Key files**
- `app.py` — FastAPI app assembly
- `dependencies.py` — singleton dependency wiring
- `routes/chat.py` — session creation, chat, history
- `routes/quiz.py` — quiz approval and answer submission
- `routes/health.py` — liveness, readiness, metrics
- `middleware/` — request logging and error handling

### 2. Core layer — `src/healthbot/core`

Provides shared runtime primitives.

**Responsibilities**
- settings management
- centralized logging
- application exceptions

**Key files**
- `settings.py` — typed environment configuration
- `logging.py` — logger setup
- `exceptions.py` — explicit domain/application failures

### 3. Domain layer — `src/healthbot/domain`

Defines state and structured contracts.

**Responsibilities**
- describe workflow state (`WorkflowState`)
- define quiz and explanation models
- provide stable internal data schemas

**Key files**
- `models.py` — `WorkflowState`
- `quiz_models.py` — structured quiz and explanation models

### 4. Infrastructure layer — `src/healthbot/infra`

Encapsulates external dependencies.

**Responsibilities**
- LLM provider (OpenAI / proxy)
- web search integration (Tavily)
- checkpointing backends
- retry / timeout configuration

**Key files**
- `llm_provider.py` — OpenAI model factory
- `web_search_tool.py` — Tavily tool wrapper

### 5. Service layer — `src/healthbot/services`

Contains business logic used by the workflow and API.

**Responsibilities**
- validate topic scope
- quiz generation and grading
- generate educational explanations
- manage session interactions with the workflow

**Key files**
- `health_validator.py`
- `quiz_service.py`
- `explanation_service.py`
- `session_service.py`

`SessionService` is the main application façade. It hides graph invocation details and normalizes workflow output for API clients.

### 6. Workflow layer — `src/healthbot/workflow`

Defines the orchestration logic.

**Responsibilities**
- register graph nodes
- declare transitions / implement routing rules
- compile the LangGraph graph construction

**Key files**
- `nodes.py` — workflow node implementations
- `router.py` — transition decisions
- `workflow_builder.py` — graph construction and compilation

### 7. Prompts layer — `src/healthbot/prompts`

Single source of truth for prompts.
**Responsibilities**
- store and version prompts
- expose typed prompt builders
- separate prompts from business logic
- support evaluation and regression testing

### 8. Repository layer — `src/healthbot/repositories`

Handles persistence.
Supported backends: in-memory (dev), SQLite (default), Redis (optional)

### 9. Observability layer — `src/healthbot/observability`

Adds runtime visibility.

**Responsibilities**
- collect metrics (counters, timers, gauges)
- trace important operations (request-level)
- support Prometheus-compatible export

**Key files**
- `metrics.py`
- `tracing.py`

### 8. Repository layer — `src/healthbot/repositories`

Currently minimal, but strategically important.

**Role**
- define persistence boundaries
- prepare the codebase for Redis, Postgres, or LangGraph checkpoint backends
- avoid coupling business logic to in-memory storage

### 9. Prompt layer — `src/healthbot/prompts`

This folder should become the **single source of truth for prompts**.

**Responsibilities**
- store system prompts and task prompts by domain
- version prompts explicitly
- expose typed prompt builders
- support testing and iterative prompt evaluation


### 10. Evaluation layer — `src/healthbot/evals`

Introduces evaluation-driven development.

**Responsibilities**
- prompt evaluation datasets 
- scoring logic (safety, grounding, refusal, keywords)
- regression detection

**Purpose**: prevent prompt regressions, measure answer quality, and support CI gating (future)

## Execution model

The current workflow is resumable and stateful:

1. A client creates a `session_id`
2. The client asks a health question
3. The workflow validates the topic
4. If valid, the agent generates an explanation
5. The workflow interrupts to ask whether a quiz should be created
6. Apply safety layer
7. If approved, the workflow generates one multiple-choice question
8. The workflow interrupts again to collect the answer
9. The answer is graded and explained

This design maps well to HTTP because interruptions are surfaced explicitly and can be resumed through dedicated API endpoints.

## Current strengths

### Clear separation of concerns
The project is well-defined layers reduce coupling and improve maintainability.

### Good prototype for LangGraph
Using a graph model that enables complex flows (interrupt/resume, tools, branching).

### Prompt centralization
Improves safety, reproducibility, and iteration speed.

### Session abstraction
`SessionService` isolates API from workflow complexity.

## Important architectural limits

### Distributed scalability
The SQLite is local and Redis/Postgres require infra setup.

### Safety is still evolving
The guardrails exist but are not fully formalized.

### Observability is not yet production-grade
No distributed tracing stack yet

### Retrieval grounding is still heuristic
Source ranking and citation formatting can improve.


## Major improvement tracks

### 1. Persistent and scalable state
- Redis (sessions) and Postgres (history + checkpoints)

### 2. Stronger prompt governance
- Versioning, A/B testing, and audit logs

### 3. Medical safety layer
- Risk classification, escalation rules, and stricter refusal policies

### 4. Ground improvements
Strengthen source usage when the agent searches the web.
- structured citations, source ranking, and evidence separation

### 5. Production observability
- OpenTelemetry, Prometheus + Grafana, and distributed tracing

### 6. Reliability around tool execution
Add defensive controls around tool calls.
- retries with backoff
- fallback behavior when tools fail

### 7. Evaluation-driven development
- CI gating on eval scores, LLM-as-a-judge, and larger datasets

### 8. Separate formatting from reasoning
- Node returns structured data and formatting handled separately

## Recommended prompt management design

A rigorous prompt architecture for this project could be:

```text
src/healthbot/prompts/
├── __init__.py
├── base.py
├── registry.py
├── versions.py
├── health_validator.py
├── health_agent.py
├── quiz_generation.py
├── quiz_explanation.py
├── safety.py
└── templates/
    ├── health_agent_v1.md
    ├── health_validator_v1.md
    ├── quiz_generation_v1.md
    └── quiz_explanation_v1.md
```

### Recommended implementation pattern

**`base.py`**
- defines a small typed prompt object, for example `PromptSpec`
- stores `name`, `version`, `system_template`, `input_variables`

**`registry.py`**
- central registry to fetch prompts by logical name
- example: `get_prompt("quiz_generation")`

**domain prompt modules**
- expose strongly typed builders such as:
  - `build_health_validator_prompt(question: str)`
  - `build_quiz_generation_prompt(summary: str)`
  - `build_quiz_explanation_prompt(...)`

**`templates/`**
- keeps long prompt text out of business code
- enables review by product, safety, and domain experts

### Example design rule

Services should never contain inline multi-line prompt strings.
They should only do this:

```python
from src.healthbot.prompts.quiz_generation import build_quiz_generation_prompt

messages = build_quiz_generation_prompt(summary)
quiz = llm_structured.invoke(messages)
```

## Proposed target architecture

```text
Client / API / CLI
       |
       v
Application services
       |
       v
Workflow orchestration
       |
       +--> domain services
       +--> prompt registry
       +--> safety layer
       +--> evaluation hooks
       +--> retrieval tools
       +--> persistence layer
       |
       v
External systems (LLM, search, DB, telemetry)
```

## Conclusion

MedLearn Agent now stands as a well-structured AI backend with:

- prompt governance 
- evaluation pipeline 
- safety-aware design 
- persistent sessions and checkpointing

The next step is to evolve toward:
1. production-grade observability
2. stronger safety enforcement
3. scalable infrastructure
4. evaluation-driven CI

Those changes would move the project from a strong prototype into a *deployable and governable AI system*.
