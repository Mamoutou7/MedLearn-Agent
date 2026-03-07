"""
Health topic validation service.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from src.healthbot.infra.llm_provider import LLMProvider
from src.healthbot.domain.models import WorkflowState


class HealthValidator:
    """
    Service responsible for validating if a question
    is related to health.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider.get_model()

    def health_validation_node(self, state: WorkflowState):
        """
        Validate a user question.

        Returns
        -------
        dict
        """
        question = state.get("question", "")

        validator_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a health topic validator. Respond YES if the question is about health, medicine or wellness. 
            Otherwise NO.
    
            Instructions:
            - Respond with ONLY "YES" if the question is health-related
            - Respond with ONLY "NO" if the question is NOT health-related
            - Be strict - only medical/health topics should be "YES"
    
            Question: {question}"""),
            ("user", "{question}")
        ])

        try:
            response = self.llm.invoke(validator_prompt.format_messages(question=question))
            decision = response.content.strip().upper()

            is_health = decision in ["YES", "Y", "TRUE", "HEALTH-RELATED"]

            if is_health:
                return {
                    "messages": [AIMessage(content="Health topic validated")],
                    "health_topic": True,
                    "answer": "Health-related topic",
                    "question": question
                }

            return {
                "messages": [AIMessage(content="Only health topics allowed.")],
                "health_topic": False,
                "answer": "Question rejected - not health-related",
                "question": question
            }

        except Exception as e:
            print(f"Error in health validation: {e}")
            return {
                "messages": [AIMessage(content="Error in validation. Please ask a health-related question.")],
                "question": question,
                "answer": "Question rejected - not health-related",
                "health_topic": False
            }

if __name__ == "__main__":
    health_validator = HealthValidator(LLMProvider())

    state = {"question": "What is Chicago?"}

    print(health_validator.health_validation_node(state))