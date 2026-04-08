from __future__ import annotations

import json
import os
from pathlib import Path

from healthbot.evals.runner import PromptEvalRunner
from healthbot.infra.llm_provider import LLMProvider


DEFAULT_THRESHOLD = float(os.getenv("EVAL_SCORE_THRESHOLD", "0.80"))


def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is missing. "
              "Skipping prompt evaluations.")
        return 0

    llm = LLMProvider().get_model()
    runner = PromptEvalRunner(llm=llm)

    project_root = Path(__file__).resolve().parents[1]
    dataset_path = (project_root / "src" / "healthbot" / "evals"
                    / "datasets" / "prompt_eval_cases.json")
    output_path = project_root / "eval_results.json"

    results = runner.run_dataset(dataset_path)

    payload = []
    scores = []

    for result in results:
        payload.append(
            {
                "case_id": result.case.case_id,
                "prompt_name": result.case.prompt_name,
                "answer": result.answer,
                "score": {
                    "total_score": result.score.total_score,
                    "keyword_score": result.score.keyword_score,
                    "safety_score": result.score.safety_score,
                    "grounding_score": result.score.grounding_score,
                    "refusal_score": result.score.refusal_score,
                    "notes": result.score.notes,
                },
            }
        )
        scores.append(result.score.total_score)

    average_score = sum(scores) / len(scores) if scores else 0.0

    output = {
        "average_score": round(average_score, 4),
        "threshold": DEFAULT_THRESHOLD,
        "results": payload,
    }

    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(f"Average score: {average_score:.4f}")
    print(f"Threshold: {DEFAULT_THRESHOLD:.4f}")
    print(f"Saved results to: {output_path}")

    return 0 if average_score >= DEFAULT_THRESHOLD else 1


if __name__ == "__main__":
    raise SystemExit(main())