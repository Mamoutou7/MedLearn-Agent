from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class EvalCase:
    """A single prompt evaluation case."""

    case_id: str
    prompt_name: str
    question: str
    expected_keywords: list[str] = field(default_factory=list)
    forbidden_keywords: list[str] = field(default_factory=list)
    must_refuse: bool = False
    must_include_disclaimer: bool = False
    expected_source_domains: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EvalScore:
    """Normalized scoring result for a generated answer."""

    case_id: str
    prompt_name: str
    total_score: float
    keyword_score: float
    safety_score: float
    grounding_score: float
    refusal_score: float
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EvalResult:
    """Full evaluation result including answer and structured score."""

    case: EvalCase
    answer: str
    score: EvalScore
    heuristic_score: float | None = None
    judge_score: float | None = None
    combined_score: float | None = None
    judge_payload: dict[str, Any] | None = None
