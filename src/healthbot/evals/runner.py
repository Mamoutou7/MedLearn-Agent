from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage

from healthbot.core.logging import get_logger
from healthbot.evals.models import EvalCase, EvalResult
from healthbot.evals.rubric import score_answer
from healthbot.services.medical_policy import MedicalPolicy
from healthbot.services.prompt_manager import PromptManager
from healthbot.services.safety_service import SafetyService

logger = get_logger(__name__)


class PromptEvalRunner:
    """Runs prompt evaluation datasets against the configured LLM."""

    def __init__(self, llm, judge: Any | None = None) -> None:
        self.llm = llm
        self.judge = judge
        self.prompt_manager = PromptManager()
        self.safety_service = SafetyService()
        self.medical_policy = MedicalPolicy()

    def load_cases(self, path: str | Path) -> list[EvalCase]:
        path = Path(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [EvalCase(**item) for item in payload]

    def build_messages(self, case: EvalCase):
        """Build prompt messages for a prompt evaluation case."""
        prompt_kwargs = {
            "question": case.question,
        }

        if case.prompt_name == "health_agent":
            prompt_kwargs["source_context"] = (
                case.source_context
                or "No external sources were retrieved for this evaluation case."
            )

        return self.prompt_manager.render(
            case.prompt_name,
            version=case.prompt_version,
            **prompt_kwargs,
        )

    def run_case(self, case: EvalCase) -> EvalResult:
        messages = self.build_messages(case)
        response = self.llm.invoke(
            messages,
            span_name=f"llm.eval.{case.prompt_name}",
        )

        answer = response.content if hasattr(response, "content") else str(response)

        if case.prompt_name == "health_agent":
            message = AIMessage(content=answer)
            message = self.safety_service.apply(message, question=case.question)
            message = self.medical_policy.enforce_on_message(message)
            answer = str(message.content)

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
            "Prompt eval completed | case_id=%s | prompt=%s | "
            "heuristic=%.3f | judge=%s | combined=%.3f",
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
