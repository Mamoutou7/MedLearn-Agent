import pytest
from langchain_core.messages import AIMessage


class FakeLLM:
    def invoke(self, messages):
        return AIMessage(content="Stub response")


class FakeLLMProvider:
    def get_model(self):
        return FakeLLM()


@pytest.fixture
def fake_llm_provider():
    return FakeLLMProvider()