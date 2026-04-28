# Changelog

All significant changes to this project will be documented here.
## [Unreleased]

### Build

- add production Dockerfile (docker)

- ignore local artifacts in Docker context (docker)

- ignore local artifacts in Github context (git)


### CI/CD

- add prompt evaluation gating workflow

- add guarded prompt evaluation job with score gating

- add guarded prompt evaluation job with score gating

- add guarded prompt evaluation job with score gating

- add guarded prompt evaluation job with score gating

- add guarded prompt evaluation job with score gating

- add guarded prompt evaluation job with score gating

- add pytest and prompt evaluation quality gate workflow

- split pipeline into lint, tests, evals, and quality summary jobs

- increase EVAL_AVG_SAFETY_SCORE variable value

- build and publish Docker image after tests and evals

- build and publish Docker image after tests and evals

- deploy staging image to Kubernetes (deploy)


### Corrections

- handle missing OpenAI API key gracefully in CI (evals)

- provider url fixed

- use average safety score for CI gating (evals)

- make safety rubric more robust for educational and red-flag cases (evals)

- make lint appropriate (evals)

- make safety rubric more robust for educational and red-flag cases (evals)

- use average grounding and combined score for CI gating (evals)

- rename threshold variables

- rename threshold env variables

- rename average grounding score threshold variables

- delete requirements file

- enable experimental debug exporter for local Alloy collector (observability)

- Define API default Key and add exceptions

- rename correctly gounding threshold variables

- rename correctly gounding threshold variable (scripts)

- ajust avg combined threshold (ci)

- enforce threshold variables (scripts)

- differentiate judge model to generator model (LLMJude, LLM) (core)

- provide source context when rendering health agent prompts (evals)

- make safety and grounding rubric more robust (evals)

- align rubric with safety and grounding behavior (evals)

- align rubric with safety and grounding behavior (evals)

- configure explicit CORS origins for production (k8s)

- use local Docker image for desktop deployment (k8s)

- configure explicit CORS origins for production (k8s)

- configure local ingress host and production CORS origins (k8s)


### Documentation

- update README file (readme)

- update readme file (readme)

- update changelog file (changelog)

- update readme file (readme)


### Features

- export eval results and fail below quality threshold (evals)

- feat (core): add config file

- solve lint erros (evals)

- export eval results and fail below configured threshold (evals)

- resolve lint errors (evals)

- enforce gating on average, safety, and refusal scores (evals)

- add robust dislaimers hints (evals)

- add evaluation dataset (data)

- add evals results (data)

- combine heuristic and llm-judge scores in eval runner (evals)

- export heuristic, judge, and combined scores in eval results (evals)

- Add judge model name (setting)

- Add LLM judge evaluation (evals)

- Add judge prompt builder (prompt)

- update evals models (evals)

- add OpenTelemetry business spans to workflow nodes (observability)

- add OpenTelemetry bootstrap and FastAPI/HTTPX instrumentation (observability)

- add business spans for session, workflow, and web search (observability)

- add OpenTelemetry bootstrap and FastAPI/HTTPX instrumentation (observability)

- add OpenTelemetry bootstrap and FastAPI/HTTPX instrumentation (observability)

- add OpenTelemetry bootstrap and FastAPI/HTTPX instrumentation (observability)

- Add OpenTelemetry dependencies (pyproject)

- add OpenTelemetry bootstrap (observability)

- add OpenTelemetry boostrap and FastAPI/HTTPX instrumentation (observability)

- wrap LLM invocations with OpenTelemetry spans (observability)

- wrap LLM invocations with OpenTelemetry spans (observability)

- add observable PromptManager for centralized prompt rendering (prompts)

- wrap LLM invocations with OpenTelemetry spans (observability)

- wrap LLM invocations with OpenTelemetry spans (observability)

- use dedicated observed judge model for LLM-as-judge scoring (evals)

- add pre-LLM safety classifier and post-LLM medical policy (safety)

- strengthen post-generation medical safety guidance (safety)

- add structured evidence packs and citation formatting (grounding)

- extend workflow state with retrieval sources and safety metadata (grounding)

- add source context support to health agent prompt (grounding)

- route validated health questions through retrieval before answer generation (grounding)

- propagate retrieval sources through workflow and compose cited answers (grounding)

- add pre-LLM safety classifier and post-LLM medical policy (safety)

- use dedicated observed judge model for LLM-as-judge scoring (evals)

- propagate retrieval sources through workflow and compose cited answers (grounding)

- add versioned prompt registry (prompts)

- add prompt version registry and configurable prompt selection (prompts)

- add prompt version registry and configurable prompt selection (prompts)

- add prompt A/B testing settings (config)

- add deterministic prompt experiment resolver (prompts)

- track prompt versions and experiment assignments in state (workflow)

- pass session id into graph state for prompt experiments (workflow)

- apply A/B prompt assignment in health agent workflow (prompts)

- export prompt version in evaluation results (evals)

- add prompts versioning (prompts)


### Maintenance

- update evaluation results with combined scoring (heuristic + judge), safety=1.0, grounding improvements pending (evals)

- delete config file (core)

- update evaluation results with combined scoring (heuristic + judge), safety=1.0, grounding improvements pending (evals)

- create file for local Alloy collector (observability)

- clean up formatting and remove inline prompt strings (prompts)

- add contextual LLM span names in domain services (observability)

- add contextual LLM span names in workflow nodes (observability)


### Others changes

- update changelog file

- update changelog file

- apply ruff fixes and formatting

- apply ruff fixes and formatting

- apply ruff fixes and formatting

- apply ruff fixes and formatting

- apply ruff fixes and formatting

- apply ruff fixes and formatting

- apply ruff fixes and formatting

- apply ruff fixes and formatting

- lint formatting (evals)

- lint formatting (services)

- nodes codes lint formatting (workflow)

- add source context

- remove healthbot_graph.png

- add base Kubernetes manifests (k8s)


### Refactoring

- harden web search tool input handling, payload validation, and observability (search)

- refactor (otel): refactor error handling message

- improve web search tool observability and robustness (search)

- improve session storage abstraction and persistence backends (repositories)

- improve session orchestration, safety, and prompt management (services)

- improve graph visuaize script (utils)

- improve routing, resilience, and observability (workflow)

- replace service default name (settings)

- render evaluation prompts through PromptManager (evals)

- render evaluation prompts through PromptManager (evals)

- add prompt versioning variable in health_agent (workflow)


### Tests

- strengthen workflow, lint, safety, eval, and repository coverage

- update fake LLM to support observed invocation kwargs (workflow)

- update fake LLMs to support observed invocation kwargs

- add versioned categorized prompt evaluation dataset (evals)



