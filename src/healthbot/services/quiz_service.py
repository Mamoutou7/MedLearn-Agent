from __future__ import annotations

from typing import Dict

from langchain_core.prompts import ChatPromptTemplate

from src.healthbot.domain.quiz_models import QuizQuestion
from src.healthbot.infra.llm_provider import LLMProvider

from src.healthbot.core.logging import get_logger
from src.healthbot.core.exceptions import QuizGenerationError, QuizGradingError

logger = get_logger(__name__)

class QuizService:
    """
    Generate quiz questions from a health summary.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider.get_model()

    def generate_quiz(self, summary: str) -> dict:
        """
        Generate a multiple-choice quiz based on a health summary.
        """

        llm_structured = self.llm.with_structured_output(QuizQuestion)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
            "system",
            """
            You are a medical educator creating a comprehension quiz.
            
            Your task:
            Generate ONE multiple-choice question based on the provided
            health information.
            
            Rules:
            - The question must test understanding of the health topic.
            - Provide exactly 4 answer choices: A, B, C, D.
            - Only ONE answer must be correct.
            - Use simple, patient-friendly language.
            - All options should be plausible but clearly different.
            
            Examples:
            
            Health Information:
            "Diabetes is a condition where blood sugar levels are too high."
            
            Quiz:
            Question: What is the main problem in diabetes?
            A: Low blood pressure
            B: High blood sugar
            C: Weak muscles
            D: Poor vision
            Correct Answer: B
            
            
            Health Information:
            "HIV attacks the immune system and weakens the body's ability to fight infections."
            
            Quiz:
            Question: What system does HIV primarily damage?
            A: Respiratory system
            B: Digestive system
            C: Immune system
            D: Nervous system
            Correct Answer: C
            
            Generate a similar quiz question based on the user's health summary.
            """
                ),
                ("user", "{summary}")
            ]
        )

        quiz = llm_structured.invoke(
            prompt.format_messages(summary=summary)
        )

        return quiz.model_dump()


class QuizApprovalService:
    """
    Service responsible for handling quiz approval logic.
    """

    def approve(self, decision: str) -> bool:
        """
        Determine whether the user approved the quiz.

        Parameters
        ----------
        decision : str
            User decision (approve / reject)

        Returns
        -------
        bool
        """

        decision = decision.lower().strip()

        return decision == "approve"


class QuizGradingService:
    """
    Service responsible for grading quiz answers.
    """

    VALID_ANSWERS = {"A", "B", "C", "D"}

    def validate_answer(self, answer: str) -> bool:
        """
        Validate user answer format.

        Returns
        -------
        bool
        """
        logger.debug(f"Validating answer: {answer}")

        return answer.upper() in self.VALID_ANSWERS

    def grade(self, user_answer: str, correct_answer: str) -> Dict:
        """
        Grade the quiz answer.

        Returns
        -------
        Dict
        """
        try:
            user_answer = user_answer.upper().strip()
            correct_answer = correct_answer.upper().strip()

            if user_answer not in self.VALID_ANSWERS:
                logger.warning("Invalid quiz answer format")

                raise QuizGradingError(
                    "Invalid quiz answer. Must be A, B, C or D."
                )

            is_correct = user_answer == correct_answer
            score = 100 if is_correct else 0

            logger.info(
                f"Quiz graded | user_answer={user_answer} | correct={is_correct}"
            )

            return {
                "is_correct": is_correct,
                "score": score,
            }
        except Exception as e:
            logger.error(
                "Quiz grading failed",
                exc_info=True
            )

            raise QuizGradingError(
                "Quiz grading failed"
            ) from e
