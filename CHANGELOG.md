# Changelog

All significant changes to this project will be documented here.

## [Unreleased]

### Build

- Add redis, postegres and langgraph-checkpoint-sqlite dependencies (deps)

- Package project properly and fix script entrypoints


### Documentation

- Update README with persistence, prompt registry, safety, and observability improvements

- Document prompt evaluation and regression workflow

- Codebase repository structure updated

- Update README with packaging, security, and runtime guidance

- Update README with packaging, security, and runtime guidance

- Refine system design with eval pipeline, safety layer, improved observability, and scalable architecture direction (architecture)

- Add automatic changelog generation (changelog)


### Fonctionnalités

- Add model name configuration (config)

- Add implementation in llm_provider (llm)

- Add models representing workflow implementation (models)

- Add tavily web search implementation (tools)

- Add health topic validator implementation (services)

- Add quiz service implementation (services)

- Update health topic validator implementation (services)

- Update quiz service implementation (services)

- Add agent running implementation (scripts)

- Add exceptions, logging implementation (core)

- Add requirement file (requirement)

- Update requirement file

- Update readme file

- Add bash automated flow file

- Update architecture file

- Update readme file (readme)

- Update architecture file (architecture)

- Centralize prompts, add base, registry and safety rules (prompts)

- Update gitignore file (git)

- Update quiz models (domain)

- Close session and checkpoint resources gracefully on shutdown (app)

- Add configurable LangGraph checkpointer factory (checkpoint)

- Add session and checkpoint backend environment settings (config)

- Add checkpoint exceptions (exception)

- Add checkpoint exceptions (exception)

- Persist agent sessions in Redis (session)

- Persist user sessions in Redis via repository abstraction (session)

- Add SQLite-backed session persistence (session)

- Add gauges, span ids, and Prometheus metrics endpoint (observability)

- Improve grounding, source quality, and medical red-flag handling (safety)

- Add prompt evaluation models, scoring rubric, and dataset runner (evals)


### Maintenance

- Initialize chatbot project structure

- Update configuration settings (config)

- Update configuration settings (config)

- Update configuration settings (config)

- Remove repositories directory


### Performances

- Aggregate timer stats instead of storing all samples in memory (metrics)


### Refactoring

- Main script refactorized (cli)

- Improve explanation_service, health_validator and quiz_service implementation (services)

- Externalize health-topic classification prompt (validator)

- Centralize quiz generation and explanation prompts (quiz)

- Centralize quiz generation and explanation prompts (quiz)

- Move HealthBot agent and welcome prompts out of nodes (workflow)

- Wire session and checkpoint backends through dependency injection (api)

- Introduce repository-based session storage (session)

- Remove hardcoded MemorySaver from WorkflowBuilder (workflow)

- Centralize rejection prompt and prompt rendering (prompts)

- Standardize package imports across source and tests


### Tests

- Add units tests (tests)

- Add coverage for Redis and in-memory session repositories (session)

- Add coverage for quiz generation flow (quiz)

- Add coverage for quiz approval workflow (quiz)

- Add coverage for quiz grading workflow (quiz)

- Add unit tests for quiz service behavior (quiz)

- Add unit tests for health topic validation (validation)

- Add regression tests for LangGraph workflow execution (workflow)

- Add prompt and safety regression coverage (regression)

- Cover session persistence and foreign key enforcement (sqlite)

- Cover shared Tavily provider and curated web search behavior (search)


### api

- Fallback to in-memory session repository when Redis is unavailable

- Return structured JSON responses for domain and unexpected errors


### config

- Add session backend fallback settings and local Redis default


### core

- Add SessionBackendUnavailableError for session storage failures


### middleware

- Improve request logging for failed and completed HTTP calls


### repo

- Wrap Redis client failures in session repository errors


### service

- Translate session repository failures into service-level backend errors



