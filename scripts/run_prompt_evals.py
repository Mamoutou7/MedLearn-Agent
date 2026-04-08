from __future__ import annotations

import json

from healthbot.core.config import DEFAULT_THRESHOLD, EVAL_BASE_DIR
from healthbot.evals.runner import PromptEvalRunner
from healthbot.infra.llm_provider import LLMProvider


def main() -> None:
    llm = LLMProvider().get_model()
    runner = PromptEvalRunner(llm=llm)


    dataset_path = (EVAL_BASE_DIR / "src" / "healthbot" / "evals"
                    / "datasets" / "prompt_eval_cases.json")
    output_path = (EVAL_BASE_DIR / "src" / "healthbot"
                   / "evals" / "datasets" / "eval_results.json")


    results = runner.run_dataset(dataset_path)

    payload = []
    scores = []

    for result in results:
        item = {
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
        payload.append(item)
        scores.append(result.score.total_score)

    average_score = sum(scores) / len(scores) if len(scores) > 0 else 0.0
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
    main()