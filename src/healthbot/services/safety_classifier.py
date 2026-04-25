from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from healthbot.core.logging import get_logger
from healthbot.observability.metrics import metrics

logger = get_logger(__name__)

SafetyCategory = Literal[
    "general",
    "emergency",
    "mental_health_crisis",
    "harmful_misinformation",
]

SafetySeverity = Literal[
    "low",
    "medium",
    "high",
    "critical",
]


@dataclass(slots=True)
class SafetyClassification:
    """Structured safety classification for a user health question."""

    category: SafetyCategory
    severity: SafetySeverity
    should_short_circuit: bool
    message: str | None = None
    matched_rules: list[str] | None = None


class SafetyClassifier:
    """Rule-based pre-LLM classifier for obvious medical safety risks."""

    def classify(self, question: str) -> SafetyClassification:
        normalized = question.lower().strip()

        if not normalized:
            return SafetyClassification(
                category="general",
                severity="low",
                should_short_circuit=False,
                matched_rules=[],
            )

        emergency = self._classify_emergency(normalized)
        if emergency is not None:
            return emergency

        mental_health = self._classify_mental_health_crisis(normalized)
        if mental_health is not None:
            return mental_health

        misinformation = self._classify_harmful_misinformation(normalized)
        if misinformation is not None:
            return misinformation

        return SafetyClassification(
            category="general",
            severity="low",
            should_short_circuit=False,
            matched_rules=[],
        )

    def _classify_emergency(self, text: str) -> SafetyClassification | None:
        emergency_rules = [
            (
                "chest_pain_breathing",
                ["chest pain"],
                ["trouble breathing", "difficulty breathing", "shortness of breath"],
                (
                    "Chest pain with trouble breathing can be a medical emergency. "
                    "Please call emergency services or seek immediate medical care now."
                ),
            ),
            (
                "stroke_symptoms",
                ["numbness on one side", "face drooping", "slurred speech"],
                [],
                (
                    "Sudden numbness, face drooping, or slurred speech can be signs of a stroke. "
                    "Please call emergency services or seek immediate medical care now."
                ),
            ),
            (
                "vomiting_blood",
                ["vomiting blood", "throwing up blood"],
                [],
                (
                    "Vomiting blood can be a serious medical emergency. "
                    "Please seek emergency medical care immediately."
                ),
            ),
            (
                "severe_abdominal_pain",
                ["severe abdominal pain"],
                ["vomiting blood", "fainting", "confusion"],
                (
                    "Severe abdominal pain with symptoms like vomiting blood, \
                    fainting, or confusion "
                    "can be urgent. Please seek immediate medical care."
                ),
            ),
        ]

        for rule_name, required_terms, optional_terms, message in emergency_rules:
            required_match = any(term in text for term in required_terms)
            optional_match = not optional_terms or any(term in text for term in optional_terms)

            if required_match and optional_match:
                logger.warning("Emergency safety rule matched: %s", rule_name)
                metrics.increment("safety.classifier.emergency")

                return SafetyClassification(
                    category="emergency",
                    severity="critical",
                    should_short_circuit=True,
                    message=message,
                    matched_rules=[rule_name],
                )

        return None

    def _classify_mental_health_crisis(self, text: str) -> SafetyClassification | None:
        crisis_terms = [
            "kill myself",
            "suicide",
            "suicidal",
            "harm myself",
            "end my life",
            "want to die",
        ]

        for term in crisis_terms:
            if term in text:
                logger.warning("Mental health crisis rule matched: %s", term)
                metrics.increment("safety.classifier.mental_health_crisis")

                return SafetyClassification(
                    category="mental_health_crisis",
                    severity="critical",
                    should_short_circuit=True,
                    message=(
                        "I'm really sorry you're feeling this way. "
                        "If you might harm yourself or feel in immediate danger, \
                        please call emergency services now. "
                        "If available in your country, contact a suicide crisis hotline \
                        or reach out to someone you trust immediately."
                    ),
                    matched_rules=[term],
                )

        return None

    def _classify_harmful_misinformation(self, text: str) -> SafetyClassification | None:
        harmful_patterns = [
            "drink bleach",
            "bleach cure",
            "stop insulin",
            "stop taking insulin",
            "ignore chest pain",
            "cure cancer with",
        ]

        for pattern in harmful_patterns:
            if pattern in text:
                logger.warning("Harmful misinformation rule matched: %s", pattern)
                metrics.increment("safety.classifier.harmful_misinformation")

                return SafetyClassification(
                    category="harmful_misinformation",
                    severity="high",
                    should_short_circuit=True,
                    message=(
                        "That approach may be dangerous. Please do not use harmful substances or \
                        stop prescribed treatment "
                        "without speaking with a qualified healthcare professional. "
                        "If this is urgent or symptoms are severe, seek medical \
                        care immediately."
                    ),
                    matched_rules=[pattern],
                )

        return None
