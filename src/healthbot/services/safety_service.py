from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from langchain_core.messages import AIMessage

from healthbot.core.logging import get_logger
from healthbot.observability.metrics import metrics

logger = get_logger(__name__)

RED_FLAG_PATTERNS = [
    r"chest pain",
    r"short(ness)? of breath|breathing (difficulty|trouble)",
    r"stroke",
    r"suicidal|suicide|self-harm",
    r"severe bleeding",
    r"loss of consciousness|passed out|fainted",
    r"seizure",
    r"anaphylaxis|severe allergic reaction",
]


@dataclass(slots=True)
class SafetyReview:
    emergency_guidance: str | None = None
    grounding_note: str | None = None


class SafetyService:
    """Adds lightweight medical-safety and grounding reinforcement to answers."""

    def review(
        self,
        question: str,
        answer: str,
        source_domains: Iterable[str] | None = None,
    ) -> SafetyReview:
        source_domains = [d for d in (source_domains or []) if d]

        emergency_guidance = None
        for pattern in RED_FLAG_PATTERNS:
            if re.search(pattern, question or "", flags=re.IGNORECASE):
                emergency_guidance = (
                    "If you have severe or rapidly worsening symptoms, seek urgent medical care "
                    "or contact local emergency services right away."
                )
                metrics.increment("safety.red_flag.detected")
                break

        grounding_note = None
        if source_domains:
            cited_domains = ", ".join(source_domains[:3])
            if cited_domains.lower() not in (answer or "").lower():
                grounding_note = f"Sources reviewed: {cited_domains}."
        else:
            grounding_note = "This answer is general educational information and is not a diagnosis."

        return SafetyReview(
            emergency_guidance=emergency_guidance,
            grounding_note=grounding_note,
        )

    def apply(
        self,
        message: AIMessage,
        question: str,
        source_domains: Iterable[str] | None = None,
    ) -> AIMessage:
        content = getattr(message, "content", None)
        if not isinstance(content, str) or getattr(message, "tool_calls", None):
            return message

        review = self.review(
            question=question,
            answer=content,
            source_domains=source_domains,
        )

        additions: list[str] = []

        if review.emergency_guidance and review.emergency_guidance.lower() not in content.lower():
            additions.append(review.emergency_guidance)

        if review.grounding_note and review.grounding_note.lower() not in content.lower():
            additions.append(review.grounding_note)

        if not additions:
            return message

        metrics.increment("safety.answer.postprocessed")
        logger.info("Applied safety and grounding reinforcement to answer")
        return AIMessage(content=f"{content.rstrip()}\n\n{' '.join(additions)}")