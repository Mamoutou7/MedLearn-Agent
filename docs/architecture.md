# MedLearn Agent Architecture

## Overview

MedLearn Agent is a **workflow-driven health education assistant**.
It combines a FastAPI delivery layer, a LangGraph orchestration layer, domain-oriented services, and lightweight observability.

The project is well positioned as a solid prototype for a production-grade AI application, with clear module boundaries and a simple resumable interaction model.

## Architecture diagram

![MedLearn Agent graph](../healthbot_graph.png)

## Design goals

The architecture aims to be:

- **modular** — each layer has a single clear responsibility
- **testable** — business logic is separated from HTTP and orchestration
- **resumable** — the quiz workflow supports interrupt/resume interactions
- **extensible** — storage, safety, evaluation, and new tools can be added later
- **operable** — logging, tracing, and metrics are already introduced

## High-level flow

```text
Client / CLI
    |
    v
FastAPI API
    |
    v
SessionService
    |
    v
LangGraph workflow
    |
    +--> Health validation
    +--> Health explanation agent
    +--> Optional web search tool
    +--> Quiz approval interrupt
    +--> Quiz generation
    +--> Quiz answer interrupt
    +--> Quiz grading + explanation
```

## Layered architecture

### 1. API layer — `src/healthbot/api`

Responsible for HTTP delivery.

**Responsibilities**
- define endpoints
- validate request and response payloads
- inject shared services
- install middleware
- expose health and metrics endpoints
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
- describe workflow state
- define quiz and explanation schemas
- provide stable internal contracts independent from transport

**Key files**
- `models.py` — `WorkflowState`
- `quiz_models.py` — structured quiz and explanation models

### 4. Infrastructure layer — `src/healthbot/infra`

Encapsulates external dependencies.

**Responsibilities**
- initialize the LLM client
- expose external tools
- isolate third-party integrations from business logic

**Key files**
- `llm_provider.py` — OpenAI model factory
- `web_search_tool.py` — Tavily tool wrapper

### 5. Service layer — `src/healthbot/services`

Contains business logic used by the workflow and API.

**Responsibilities**
- validate topic scope
- generate quizzes
- grade answers
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
- declare transitions
- implement routing rules
- compile the LangGraph graph

**Key files**
- `nodes.py` — workflow node implementations
- `router.py` — transition decisions
- `workflow_builder.py` — graph construction and compilation

### 7. Observability layer — `src/healthbot/observability`

Adds runtime visibility.

**Responsibilities**
- collect counters and timings
- trace important operations
- support debugging and basic monitoring

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

**Target responsibilities**
- store system prompts and task prompts by domain
- version prompts explicitly
- expose typed prompt builders
- support testing and iterative prompt evaluation

## Execution model

The current workflow is resumable and stateful:

1. A client creates a `session_id`
2. The client asks a health question
3. The workflow validates the topic
4. If valid, the agent generates an explanation
5. The workflow interrupts to ask whether a quiz should be created
6. If approved, the workflow generates one multiple-choice question
7. The workflow interrupts again to collect the answer
8. The answer is graded and explained
9. The workflow returns a final educational response

This design maps well to HTTP because interruptions are surfaced explicitly and can be resumed through dedicated API endpoints.

## Current strengths

### Clear separation of concerns
The project already separates API, orchestration, services, infrastructure, and observability in a disciplined way.

### Good prototype for LangGraph
Using a graph rather than a loose chain is the right choice for interrupt/resume quiz flows.

### Structured outputs for quiz artifacts
The use of Pydantic models for quiz and explanation generation is a strong design choice.

### Session façade for the API
`SessionService` keeps route handlers thin and isolates workflow-specific handling.

## Important architectural limits

### In-memory state
Session and graph state are process-local. This prevents horizontal scaling and causes state loss on restart.

### Prompt logic is scattered
Prompts are embedded directly inside services and nodes, which makes versioning, testing, and governance difficult.

### Safety and grounding are still lightweight
For a health-related assistant, the current architecture does not yet enforce a strong safety layer, source attribution policy, or escalation rules.

### Observability is local only
The current metrics/tracing approach is useful for development but not enough for production monitoring.

### Delivery and domain are still somewhat coupled
Some workflow decisions and user-facing content formatting remain inside node implementations rather than dedicated response/presentation helpers.

## Serious improvement tracks

### 1. Add persistent session and checkpoint storage
Replace in-memory state with a real backend.

**Recommended options**
- Redis for active session state
- Postgres for durable conversation history
- LangGraph checkpoint persistence for resumable workflows

**Why it matters**
- survives restarts
- supports multiple API instances
- enables auditability and replay

### 2. Centralize prompt management
Move all prompts to `src/healthbot/prompts` with explicit builders and versioning.

**Why it matters**
- safer prompt changes
- easier A/B testing
- cleaner service code
- reproducible evaluations

### 3. Introduce a dedicated medical safety layer
Add a pre-response and post-response safety policy.

**Examples**
- emergency symptom detection and escalation
- scope restriction for diagnosis/treatment claims
- medication and dosage caution rules
- mandatory “educational, not medical advice” framing where appropriate

### 4. Ground answers more reliably
Strengthen source usage when the agent searches the web.

**Recommended changes**
- normalize search results into a source model
- rank and filter domains
- require citations in final answers when external search is used
- separate “retrieval evidence” from “final answer rendering”

### 5. Make observability production-ready
Move from local helpers to standard telemetry.

**Recommended changes**
- OpenTelemetry traces
- Prometheus-compatible metrics
- request and session correlation IDs
- LLM latency, token, tool, and error dashboards

### 6. Harden reliability around LLM/tool execution
Add defensive controls around model and tool calls.

**Recommended changes**
- explicit timeouts
- retries with backoff
- fallback behavior when Tavily or OpenAI fails
- better error taxonomy and user-safe messages

### 7. Improve testing strategy
Strengthen both code quality and behavior validation.

**Recommended tests**
- prompt snapshot tests
- workflow interrupt/resume integration tests
- contract tests for API schemas
- failure-path tests for tools and providers
- evaluation datasets for answer quality and safety

### 8. Separate formatting from reasoning
Keep workflow state updates focused on decisions and data, not presentation.

**Target direction**
- node returns structured data
- presenter/formatter builds user-facing text
- API can later support multiple clients and locales more easily

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

### Additional prompt governance recommendations

- version every prompt explicitly
- log prompt name and version during execution
- add snapshot tests for prompts
- maintain a small evaluation dataset for regressions
- separate system instructions from dynamic user context
- isolate safety overlays from task prompts

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
       +--> safety policy layer
       +--> retrieval/tool adapters
       +--> persistence repositories
       |
       v
External systems (OpenAI, Tavily, Redis, Postgres, telemetry)
```

## Conclusion

MedLearn Agent already has a sound structure for a serious AI backend prototype.
The most important next steps are not cosmetic; they are architectural:

1. persistent state and checkpoints
2. centralized prompt management
3. medical safety and grounding
4. stronger observability and reliability
5. evaluation-driven development

Those changes would move the project from a clean prototype toward a deployable and governable AI service.
