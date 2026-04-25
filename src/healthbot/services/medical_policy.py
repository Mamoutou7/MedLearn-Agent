from __future__ import annotations

from dataclasses import dataclass, field

from langchain_core.messages import AIMessage

from healthbot.core.logging import get_logger
from healthbot.observability.metrics import metrics

logger = get_logger(__name__)


@dataclass(slots=True)
class MedicalPolicyResult:
    """Result of post-generation medical policy validation."""

    is_safe: bool
    violations: list[str] = field(default_factory=list)


class MedicalPolicy:
    """Post-LLM safety policy for health answers."""

    FORBIDDEN_PATTERNS = [
        "you definitely have",
        "you certainly have",
        "this means you have",
        "stop taking your medication",
        "stop your medication",
        "increase your dose",
        "double your dose",
        "ignore the symptoms",
        "no need to see a doctor",
        "do not seek medical care",
    ]

    DOSAGE_RISK_PATTERNS = [
        "take 2 pills",
        "take two pills",
        "take 3 pills",
        "take three pills",
        "mg per kg",
        "increase to",
        "decrease to",
    ]

    REQUIRED_CAUTION_HINTS = [
        "healthcare professional",
        "doctor",
        "medical professional",
        "seek medical care",
        "emergency services",
    ]

    def validate_answer(self, answer: str) -> MedicalPolicyResult:
        normalized = answer.lower()
        violations: list[str] = []

        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern in normalized:
                violations.append(f"forbidden_pattern:{pattern}")

        for pattern in self.DOSAGE_RISK_PATTERNS:
            if pattern in normalized:
                violations.append(f"dosage_risk:{pattern}")

        is_safe = not violations

        if violations:
            logger.warning("Medical policy violations detected: %s", violations)
            metrics.increment("medical_policy.violations")

        return MedicalPolicyResult(
            is_safe=is_safe,
            violations=violations,
        )

    def enforce_on_message(self, message: AIMessage) -> AIMessage:
        """Validate an AIMessage and replace it with a safe fallback if needed."""
        content = message.content if isinstance(message.content, str) else str(message.content)
        result = self.validate_answer(content)

        if result.is_safe:
            return message

        safe_content = (
            "I want to keep this safe and educational. "
            "I can't provide a definite diagnosis, personalized medication changes, \
            or dosage instructions. "
            "Please speak with a qualified healthcare professional for personalized guidance. "
            "If symptoms are severe, sudden, or worsening, seek urgent medical care."
        )

        return AIMessage(
            content=safe_content,
            additional_kwargs=message.additional_kwargs,
            response_metadata=message.response_metadata,
        )
