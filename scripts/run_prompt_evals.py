from __future__ import annotations

from pathlib import Path

from src.healthbot.evals.runner import PromptEvalRunner
from src.healthbot.infra.llm_provider import LLMProvider


def main() -> None:
    llm = LLMProvider().get_model()
    runner = PromptEvalRunner(llm=llm)

    dataset_path = Path("src/healthbot/evals/datasets/prompt_eval_cases.json")
    results = runner.run_dataset(dataset_path)

    print("=" * 80)
    print("PROMPT EVALUATION RESULTS")
    print("=" * 80)

    total = 0.0
    for result in results:
        total += result.score.total_score
        print(f"[{result.case.case_id}] prompt={result.case.prompt_name}")
        print(f"score={result.score.total_score:.3f}")
        if result.score.notes:
            print("notes:")
            for note in result.score.notes:
                print(f"  - {note}")
        print(f"answer: {result.answer[:300]}")
        print("-" * 80)

    avg = total / len(results) if results else 0.0
    print(f"Average score: {avg:.3f}")


if __name__ == "__main__":
    main()