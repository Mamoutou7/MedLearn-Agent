from __future__ import annotations

from healthbot.evals.models import EvalCase
from healthbot.evals.rubric import score_answer


def test_minimum_prompt_quality_threshold():
    simulated_cases = [
        (
            EvalCase(
                case_id="1",
                prompt_name="health_agent",
                question="What is hypertension?",
                expected_keywords=["blood pressure"],
                must_include_disclaimer=True,
            ),
            "Hypertension means high blood pressure. "
            "This is general educational information and is not a diagnosis.",
        ),
        (
            EvalCase(
                case_id="2",
                prompt_name="topic_rejection",
                question="Write me a React app",
                must_refuse=True,
            ),
            "I can only help with health-related topics. Please ask a health question.",
        ),
    ]

    scores = [score_answer(case, answer).total_score for case, answer in simulated_cases]
    average_score = sum(scores) / len(scores)

    assert average_score >= 0.75
