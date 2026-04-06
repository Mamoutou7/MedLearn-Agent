from __future__ import annotations

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def quiz_summary() -> str:
    return "HIV attacks the immune system."


@pytest.fixture
def generated_quiz() -> dict:
    return {
        "question": "What system does HIV attack?",
        "option_a": "Digestive system",
        "option_b": "Immune system",
        "option_c": "Respiratory system",
        "option_d": "Nervous system",
        "correct_answer": "B",
    }


@pytest.fixture
def generated_quiz_model(generated_quiz: dict):
    model = MagicMock()
    model.model_dump.return_value = generated_quiz
    return model
