"""
Service responsible for generating detailed explanations for quiz results.

This service uses the LLM to provide educational feedback to the user
after they answer a quiz question. It explains the reasoning, reinforces
key health concepts, and provides learning tips.

Responsibilities
----------------
- Generate explanation after quiz grading
- Reinforce important health concepts
- Provide patient-friendly feedback
- Structure output using Pydantic models
"""

from __future__ import annotations

from typing import Dict

from langchain_core.prompts import ChatPromptTemplate

from src.healthbot.domain.quiz_models import QuizExplanation
from src.healthbot.infra.llm_provider import LLMProvider
from src.healthbot.core.logging import get_logger
from src.healthbot.core.exceptions import LLMServiceError
from src.healthbot.observability.metrics import metrics
from src.healthbot.observability.tracing import trace_span

logger = get_logger(__name__)


class ExplanationService:
    """
    Service responsible for generating quiz explanations.

    This service encapsulates all logic related to creating
    educational explanations after a quiz has been graded.
    """

    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize the explanation service.

        Parameters
        ----------
        llm_provider : LLMProvider
            Provider responsible for creating LLM instances.
        """
        self.llm = llm_provider.get_model()

    def generate_explanation(
        self,
        quiz_question: str,
        user_answer: str,
        correct_answer: str,
        is_correct: bool,
        summary: str,
    ) -> Dict:
        """
        Generate a structured explanation for a quiz answer.

        Parameters
        ----------
        quiz_question : str
            The quiz question shown to the user.

        user_answer : str
            The answer provided by the user.

        correct_answer : str
            The correct quiz answer.

        is_correct : bool
            Indicates whether the user answer was correct.

        summary : str
            Health information summary used to generate the quiz.

        Returns
        -------
        Dict
            Structured explanation including reasoning,
            key concepts, citations and learning tips.

        Raises
        ------
        LLMServiceError
            If the LLM invocation fails.
        """

        logger.info("Generating quiz explanation")

        try:
            with trace_span("quiz.explanation"):
                metrics.increment("quiz.explanation.calls")
                llm_structured = self.llm.with_structured_output(QuizExplanation)
                prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            """You are a medical educator helping patients understand quiz results.
    
                        Provide:
                        1. Clear explanation of the correct answer
                        2. Important health concepts
                        3. Supporting references from the summary
                        4. Tips to help remember the concept
                        
                        Use simple patient-friendly language.
                    """,
                        ),
                        (
                            "user",
                            """Create a detailed explanation for this quiz question.
                        Question: {quiz_question}
                        User Answer: {user_answer}
                        Correct Answer: {correct_answer}
                        Was Correct: {is_correct}
                        Health Summary: {summary}
                        """,
                        ),
                    ]
                )

                formatted_messages = prompt.format_messages(
                    quiz_question=quiz_question,
                    user_answer=user_answer,
                    correct_answer=correct_answer,
                    is_correct=is_correct,
                    summary=summary,
                )
                explanation = llm_structured.invoke(formatted_messages)
                logger.info("Quiz explanation generated successfully")
                return explanation.model_dump()

        except Exception as exc:
            logger.exception("Failed to generate explanation")
            metrics.increment("quiz.explanation.errors")
            raise LLMServiceError(
                "Explanation generation failed",
                context={
                    "quiz_question": quiz_question,
                    "user_answer": user_answer,
                },
            ) from exc
