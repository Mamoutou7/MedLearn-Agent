## [unreleased]

### 🚀 Features

- *(config)* Add model name configuration
- *(llm)* Add implementation in llm_provider
- *(models)* Add models representing workflow implementation
- *(tools)* Add tavily web search implementation
- *(services)* Add health topic validator implementation
- *(services)* Add quiz service implementation
- *(services)* Update health topic validator implementation
- *(services)* Update quiz service implementation
- *(scripts)* Add agent running implementation
- *(core)* Add exceptions, logging implementation
- *(requirement)* Add requirement file
- Update requirement file
- Update readme file
- Add bash automated flow file
- Update architecture file
- *(readme)* Update readme file
- *(architecture)* Update architecture file
- *(prompts)* Centralize prompts, add base, registry and safety rules
- *(git)* Update gitignore file
- *(domain)* Update quiz models
- *(app)* Close session and checkpoint resources gracefully on shutdown
- *(checkpoint)* Add configurable LangGraph checkpointer factory
- *(config)* Add session and checkpoint backend environment settings
- *(exception)* Add checkpoint exceptions
- *(exception)* Add checkpoint exceptions
- *(session)* Persist agent sessions in Redis
- *(session)* Persist user sessions in Redis via repository abstraction
- *(session)* Add SQLite-backed session persistence
- *(observability)* Add gauges, span ids, and Prometheus metrics endpoint
- *(safety)* Improve grounding, source quality, and medical red-flag handling
- *(evals)* Add prompt evaluation models, scoring rubric, and dataset runner

### 💼 Other

- *(deps)* Add redis, postegres and langgraph-checkpoint-sqlite dependencies
- Add session backend fallback settings and local Redis default
- Add SessionBackendUnavailableError for session storage failures
- Wrap Redis client failures in session repository errors
- Fallback to in-memory session repository when Redis is unavailable
- Translate session repository failures into service-level backend errors
- Return structured JSON responses for domain and unexpected errors
- Improve request logging for failed and completed HTTP calls
- Package project properly and fix script entrypoints

### 🚜 Refactor

- *(cli)* Main script refactorized
- *(services)* Improve explanation_service, health_validator and quiz_service implementation
- *(validator)* Externalize health-topic classification prompt
- *(quiz)* Centralize quiz generation and explanation prompts
- *(quiz)* Centralize quiz generation and explanation prompts
- *(workflow)* Move HealthBot agent and welcome prompts out of nodes
- *(api)* Wire session and checkpoint backends through dependency injection
- *(session)* Introduce repository-based session storage
- *(workflow)* Remove hardcoded MemorySaver from WorkflowBuilder
- *(prompts)* Centralize rejection prompt and prompt rendering
- Standardize package imports across source and tests

### 📚 Documentation

- Update README with persistence, prompt registry, safety, and observability improvements
- Document prompt evaluation and regression workflow
- Codebase repository structure updated
- Update README with packaging, security, and runtime guidance
- Update README with packaging, security, and runtime guidance
- *(architecture)* Refine system design with eval pipeline, safety layer, improved observability, and scalable architecture direction

### ⚡ Performance

- *(metrics)* Aggregate timer stats instead of storing all samples in memory

### 🧪 Testing

- *(tests)* Add units tests
- *(session)* Add coverage for Redis and in-memory session repositories
- *(quiz)* Add coverage for quiz generation flow
- *(quiz)* Add coverage for quiz approval workflow
- *(quiz)* Add coverage for quiz grading workflow
- *(quiz)* Add unit tests for quiz service behavior
- *(validation)* Add unit tests for health topic validation
- *(workflow)* Add regression tests for LangGraph workflow execution
- *(regression)* Add prompt and safety regression coverage
- *(sqlite)* Cover session persistence and foreign key enforcement
- *(search)* Cover shared Tavily provider and curated web search behavior

### ⚙️ Miscellaneous Tasks

- Initialize chatbot project structure
- *(config)* Update configuration settings
- *(config)* Update configuration settings
- *(config)* Update configuration settings
- Remove repositories directory
