# Changelog

All significant changes to this project will be documented here.
## [Unreleased]

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


### Documentation

- update README file (readme)

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


### Maintenance

- update evaluation results with combined scoring (heuristic + judge), safety=1.0, grounding improvements pending (evals)

- delete config file (core)

- update evaluation results with combined scoring (heuristic + judge), safety=1.0, grounding improvements pending (evals)


### Others changes

- update changelog file

- update changelog file



