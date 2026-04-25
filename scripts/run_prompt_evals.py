from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from healthbot.evals.judge import LLMJudge
from healthbot.evals.runner import PromptEvalRunner
from healthbot.infra.llm_provider import LLMProvider

load_dotenv()

AVG_COMBINED_SCORE_THRESHOLD = float(os.getenv("AVG_COMBINED_SCORE_THRESHOLD"))
AVG_SAFETY_SCORE_THRESHOLD = float(os.getenv("AVG_SAFETY_SCORE_THRESHOLD"))
AVG_MIN_REFUSAL_SCORE_THRESHOLD = float(os.getenv("AVG_MIN_REFUSAL_SCORE_THRESHOLD"))
AVG_GROUNDING_SCORE_THRESHOLD = float(os.getenv("AVG_GROUNDING_SCORE_THRESHOLD"))


def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        if os.getenv("CI") == "true":
            print("OPENAI_API_KEY is missing in CI.")
            return 1
        print("OPENAI_API_KEY is missing. Skipping prompt evaluations.")
        return 0

    llm = LLMProvider().get_model()

    judge = None
    if os.getenv("ENABLE_LLM_JUDGE", "false").lower() == "true":
        judge = LLMJudge(llm=llm)

    runner = PromptEvalRunner(llm=llm, judge=judge)

    project_root = Path(__file__).resolve().parents[1]
    dataset_path = (
        project_root / "src" / "healthbot" / "evals" / "datasets" / "prompt_eval_cases.json"
    )
    output_path = project_root / "eval_results.json"

    results = runner.run_dataset(dataset_path)

    payload = []
    total_scores: list[float] = []
    safety_scores: list[float] = []
    refusal_scores: list[float] = []
    grounding_scores: list[float] = []
    heuristic_scores: list[float] = []
    judge_scores: list[float] = []
    combined_scores: list[float] = []

    for result in results:
        heuristic_score = getattr(result, "heuristic_score", result.score.total_score)
        judge_score = getattr(result, "judge_score", None)
        combined_score = getattr(result, "combined_score", result.score.total_score)
        judge_payload = getattr(result, "judge_payload", None)

        total_scores.append(combined_score)
        combined_scores.append(combined_score)
        heuristic_scores.append(heuristic_score)
        safety_scores.append(result.score.safety_score)
        grounding_scores.append(result.score.grounding_score)

        if judge_score is not None:
            judge_scores.append(judge_score)

        if result.case.must_refuse:
            refusal_scores.append(result.score.refusal_score)

        payload.append(
            {
                "case_id": result.case.case_id,
                "prompt_name": result.case.prompt_name,
                "question": result.case.question,
                "answer": result.answer,
                "heuristic_score": round(heuristic_score, 4),
                "judge_score": round(judge_score, 4) if judge_score is not None else None,
                "combined_score": round(combined_score, 4),
                "judge_payload": judge_payload,
                "score": {
                    "total_score": round(result.score.total_score, 4),
                    "keyword_score": round(result.score.keyword_score, 4),
                    "safety_score": round(result.score.safety_score, 4),
                    "grounding_score": round(result.score.grounding_score, 4),
                    "refusal_score": round(result.score.refusal_score, 4),
                    "notes": result.score.notes,
                },
            }
        )

    average_safety_score = sum(safety_scores) / len(safety_scores) if safety_scores else 0.0
    min_refusal_score = min(refusal_scores) if refusal_scores else 1.0
    average_grounding_score = (
        sum(grounding_scores) / len(grounding_scores) if grounding_scores else 0.0
    )
    average_heuristic_score = (
        sum(heuristic_scores) / len(heuristic_scores) if heuristic_scores else 0.0
    )
    average_judge_score = sum(judge_scores) / len(judge_scores) if judge_scores else None
    average_combined_score = sum(combined_scores) / len(combined_scores) if combined_scores else 0.0

    checks = {
        "average_combined_score": average_combined_score >= AVG_COMBINED_SCORE_THRESHOLD,
        "average_safety_score_passed": average_safety_score >= AVG_SAFETY_SCORE_THRESHOLD,
        "min_refusal_score_passed": min_refusal_score >= AVG_MIN_REFUSAL_SCORE_THRESHOLD,
        "average_grounding_score": average_grounding_score >= AVG_GROUNDING_SCORE_THRESHOLD,
    }

    output = {
        "average_score": round(average_combined_score, 4),
        "average_heuristic_score": round(average_heuristic_score, 4),
        "average_judge_score": round(average_judge_score, 4)
        if average_judge_score is not None
        else None,
        "average_combined_score": round(average_combined_score, 4),
        "average_safety_score": round(average_safety_score, 4),
        "min_refusal_score": round(min_refusal_score, 4),
        "avg_combined_score_threshold": AVG_COMBINED_SCORE_THRESHOLD,
        "avg_safety_threshold": AVG_SAFETY_SCORE_THRESHOLD,
        "avg_min_refusal_threshold": AVG_MIN_REFUSAL_SCORE_THRESHOLD,
        "avg_grounding_threshold": AVG_GROUNDING_SCORE_THRESHOLD,
        "llm_judge_enabled": judge is not None,
        "checks": checks,
        "results": payload,
    }
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(f"Average heuristic score: {average_heuristic_score:.4f}")
    if average_judge_score is not None:
        print(f"Average judge score: {average_judge_score:.4f}")
    print(
        f"Average combined score: {average_combined_score:.4f} "
        f"(threshold={AVG_COMBINED_SCORE_THRESHOLD:.4f})"
    )
    print(
        f"Average safety score: {average_safety_score:.4f} "
        f"(threshold={AVG_SAFETY_SCORE_THRESHOLD:.4f})"
    )
    print(
        f"Average grounding score: {average_grounding_score:.4f} "
        f"(threshold={AVG_GROUNDING_SCORE_THRESHOLD:.4f})"
    )
    print(
        f"Min refusal score: {min_refusal_score:.4f} "
        f"(threshold={AVG_MIN_REFUSAL_SCORE_THRESHOLD:.4f})"
    )

    print(f"Saved results to: {output_path}")

    all_checks_passed = all(checks.values())
    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
