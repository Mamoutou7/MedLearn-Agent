"""
Pydantic domain used for structured LLM outputs.
"""
from typing import Literal

from pydantic import BaseModel


class QuizQuestion(BaseModel):
    question: str

    option_a: str
    option_b: str
    option_c: str
    option_d: str

    correct_answer: Literal["A", "B", "C", "D"]


class QuizExplanation(BaseModel):
    explanation: str
    key_concepts: str
    citations: str
    learning_tips: str
