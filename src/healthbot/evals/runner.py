from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from healthbot.core.logging import get_logger
from healthbot.evals.models import EvalCase, EvalResult
from healthbot.evals.rubric import score_answer
from healthbot.services.prompt_manager import PromptManager

logger = get_logger(__name__)


class PromptEvalRunner:
    """Runs prompt evaluation datasets against the configured LLM."""

    def __init__(self, llm, judge: Any | None = None) -> None:
        self.llm = llm
        self.judge = judge
        self.prompt_manager = PromptManager()

    def load_cases(self, path: str | Path) -> list[EvalCase]:
        path = Path(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [EvalCase(**item) for item in payload]

    def build_messages(self, case: EvalCase):
        return self.prompt_manager.render(
            case.prompt_name,
            question=case.question,
        )

    def run_case(self, case: EvalCase) -> EvalResult:
        messages = self.build_messages(case)
        response = self.llm.invoke(
            messages,
            span_name=f"llm.eval.{case.prompt_name}",
        )

        answer = response.content if hasattr(response, "content") else str(response)

        score = score_answer(case, answer)
        heuristic_score = score.total_score

        judge_score: float | None = None
        judge_payload: dict[str, Any] | None = None

        if self.judge is not None:
            try:
                judge_payload = self.judge.evaluate(
                    question=case.question,
                    answer=answer,
                )
                judge_score = float(judge_payload.get("overall_score", 0.0))
            except Exception:
                logger.exception(
                    "LLM judge evaluation failed | case_id=%s | prompt=%s",
                    case.case_id,
                    case.prompt_name,
                )

        if judge_score is not None:
            combined_score = round((heuristic_score * 0.6) + (judge_score * 0.4), 4)
            score.total_score = combined_score
            score.notes.append(
                f"Combined score used: heuristic={heuristic_score:.4f}, judge={judge_score:.4f}"
            )
        else:
            combined_score = heuristic_score

        logger.info(
            "Prompt eval completed | case_id=%s | prompt=%s | heuristic=%.3f | judge=%s | combined=%.3f",
            case.case_id,
            case.prompt_name,
            heuristic_score,
            f"{judge_score:.3f}" if judge_score is not None else "n/a",
            combined_score,
        )

        return EvalResult(
            case=case,
            answer=answer,
            score=score,
            heuristic_score=heuristic_score,
            judge_score=judge_score,
            combined_score=combined_score,
            judge_payload=judge_payload,
        )

    def run_dataset(self, path: str | Path) -> list[EvalResult]:
        cases = self.load_cases(path)
        return [self.run_case(case) for case in cases]