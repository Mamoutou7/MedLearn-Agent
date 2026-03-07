"""
Service responsible for generating quiz questions.
"""

from langchain_core.prompts import ChatPromptTemplate
from src.healthbot.domain.quiz_models import QuizQuestion
from src.healthbot.infra.llm_provider import LLMProvider


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


if __name__ == "__main__":
    quiz_service = QuizService(LLMProvider())

    summary = """
    HIV is a virus that attacks the immune system.
    If untreated, it can lead to AIDS. Treatment with antiretroviral
    medication allows people with HIV to live long and healthy lives.
    """

    result = quiz_service.generate_quiz(summary)

    print("\nGenerated Quiz:\n")
    print(result)