from __future__ import annotations

import json
from pathlib import Path

from healthbot.core.logging import get_logger
from healthbot.evals.models import EvalCase, EvalResult
from healthbot.evals.rubric import score_answer
from healthbot.prompts.health_agent import build_health_agent_messages
from healthbot.prompts.rejection import build_rejection_messages

logger = get_logger(__name__)


class PromptEvalRunner:
    """Runs prompt evaluation datasets against the configured LLM."""

    def __init__(self, llm) -> None:
        self.llm = llm

    def load_cases(self, path: str | Path) -> list[EvalCase]:
        path = Path(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [EvalCase(**item) for item in payload]

    def build_messages(self, case: EvalCase):
        if case.prompt_name == "topic_rejection":
            return build_rejection_messages(question=case.question)
        if case.prompt_name == "health_agent":
            return build_health_agent_messages(question=case.question)
        raise ValueError(f"Unsupported prompt for eval: {case.prompt_name}")

    def run_case(self, case: EvalCase) -> EvalResult:
        messages = self.build_messages(case)
        response = self.llm.invoke(messages)

        answer = response.content if hasattr(response, "content") else str(response)
        score = score_answer(case, answer)

        logger.info(
            "Prompt eval completed | case_id=%s | prompt=%s | score=%.3f",
            case.case_id,
            case.prompt_name,
            score.total_score,
        )
        return EvalResult(case=case, answer=answer, score=score)

    def run_dataset(self, path: str | Path) -> list[EvalResult]:
        cases = self.load_cases(path)
        return [self.run_case(case) for case in cases]