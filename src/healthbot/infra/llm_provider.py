from langchain_openai import ChatOpenAI
from src.healthbot.core.settings import settings

class LLMProvider:
    """
    Factory responsible for creating LLM instances.
    """

    def __init__(self):
        self._llm = None

    def get_model(self) -> ChatOpenAI:
        """
        Return configured ChatOpenAI instance.

        Returns
        -------
        ChatOpenAI
        """
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=settings.model_name,
                temperature=0,
                api_key=settings.openai_api_key
            )

        return self._llm