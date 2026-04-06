# Changelog

All significant changes to this project will be documented here.
## [Unreleased]

### Build

- add redis, postegres and langgraph-checkpoint-sqlite dependencies (deps)

- package project properly and fix script entrypoints


### Documentation

- update README with persistence, prompt registry, safety, and observability improvements

- document prompt evaluation and regression workflow

- codebase repository structure updated

- update README with packaging, security, and runtime guidance

- update README with packaging, security, and runtime guidance

- refine system design with eval pipeline, safety layer, improved observability, and scalable architecture direction (architecture)

- add automatic changelog generation (changelog)

- add automatic changelog generation (changelog)

- add automatic changelog generation (changelog)


### Features

- add model name configuration (config)

- add implementation in llm_provider (llm)

- add models representing workflow implementation (models)

- add tavily web search implementation (tools)

- add health topic validator implementation (services)

- add quiz service implementation (services)

- update health topic validator implementation (services)

- update quiz service implementation (services)

- Add agent running implementation (scripts)

- Add exceptions, logging implementation (core)

- add requirement file (requirement)

- update requirement file

- update readme file

- add bash automated flow file

- update architecture file

- update readme file (readme)

- update architecture file (architecture)

- Centralize prompts, add base, registry and safety rules (prompts)

- update gitignore file (git)

- update quiz models (domain)

- close session and checkpoint resources gracefully on shutdown (app)

- add configurable LangGraph checkpointer factory (checkpoint)

- add session and checkpoint backend environment settings (config)

- add checkpoint exceptions (exception)

- add checkpoint exceptions (exception)

- persist agent sessions in Redis (session)

- persist user sessions in Redis via repository abstraction (session)

- add SQLite-backed session persistence (session)

- add gauges, span ids, and Prometheus metrics endpoint (observability)

- improve grounding, source quality, and medical red-flag handling (safety)

- add prompt evaluation models, scoring rubric, and dataset runner (evals)

- align API routes, tests, and workflow behavior (api)


### Maintenance

- initialize chatbot project structure

- update configuration settings (config)

- update configuration settings (config)

- update configuration settings (config)

- remove repositories directory


### Others changes

- Initial commit

- update gitignore file

- facilitate modules importation

- add session backend fallback settings and local Redis default

- add SessionBackendUnavailableError for session storage failures

- wrap Redis client failures in session repository errors

- fallback to in-memory session repository when Redis is unavailable

- translate session repository failures into service-level backend errors

- return structured JSON responses for domain and unexpected errors

- improve request logging for failed and completed HTTP calls


### Performances

- aggregate timer stats instead of storing all samples in memory (metrics)


### Refactoring

- Main script refactorized (cli)

- improve explanation_service, health_validator and quiz_service implementation (services)

- externalize health-topic classification prompt (validator)

- centralize quiz generation and explanation prompts (quiz)

- centralize quiz generation and explanation prompts (quiz)

- move HealthBot agent and welcome prompts out of nodes (workflow)

- wire session and checkpoint backends through dependency injection (api)

- introduce repository-based session storage (session)

- remove hardcoded MemorySaver from WorkflowBuilder (workflow)

- centralize rejection prompt and prompt rendering (prompts)

- standardize package imports across source and tests

- reorganize test suite into e2e, integration, unit, and regression layers (tests)


### Tests

- Add units tests (tests)

- add coverage for Redis and in-memory session repositories (session)

- add coverage for quiz generation flow (quiz)

- add coverage for quiz approval workflow (quiz)

- add coverage for quiz grading workflow (quiz)

- add unit tests for quiz service behavior (quiz)

- add unit tests for health topic validation (validation)

- add regression tests for LangGraph workflow execution (workflow)

- add prompt and safety regression coverage (regression)

- cover session persistence and foreign key enforcement (sqlite)

- cover shared Tavily provider and curated web search behavior (search)



