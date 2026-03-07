"""
Service responsible for generating quiz questions.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage

from src.healthbot.infra.llm_provider import LLMProvider
from src.healthbot.domain.quiz_models import QuizQuestion
from src.healthbot.domain.models import WorkflowState

import warnings
warnings.filterwarnings("ignore")


class QuizService:
    """
    Generate quiz questions from a health summary.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider.get_model()

    def quiz_generation_node(self, state: WorkflowState):
        """
        Generate a single, relevant quiz question based on the latest AI message (summary).
        This node creates a comprehension check question based on the summary content.
        """
        messages = state["messages"]

        summary = next(
            (
                m.content
                for m in reversed(messages)
                if isinstance(m, AIMessage) and m.content
            ),
            ""
        )

        llm_structured = self.llm.with_structured_output(QuizQuestion)

        quiz_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a medical educator creating a comprehension check question. 
            Generate ONE multiple choice question based on the provided health information.

            Guidelines:
            - Make the question clear and relevant to the health information
            - Ensure only ONE answer is correct
            - Use simple, patient-friendly language
            - Focus on key concepts that patients should remember
            - Make all options plausible but only one correct

            Question Requirements:
            - Question should test understanding of important health concepts
            - All options (A, B, C, D) should be clearly different
            - Correct answer should be unambiguous
            - Question should be educational and informative
            """
             ),
            ("user", "{summary}")
        ])

        quiz = llm_structured.invoke(
            quiz_prompt.format_messages(summary=summary)
        ).model_dump()

        quiz_text = f"""
            QUIZ

            {quiz['question']}

            A) {quiz['option_a']}
            B) {quiz['option_b']}
            C) {quiz['option_c']}
            D) {quiz['option_d']}

            Reply with A, B, C or D.
            """

        return {
            "messages": [AIMessage(content=quiz_text)],
            "quiz_generated": True,
            "quiz_question": quiz_text,
            "quiz_correct_answer": quiz['correct_answer']
        }
