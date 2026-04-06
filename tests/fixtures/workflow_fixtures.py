from __future__ import annotations

import pytest
from langchain_core.messages import AIMessage


class WorkflowFakeLLM:
    def invoke(self, _messages):
        return AIMessage(content="Stub response")


class WorkflowFakeLLMProvider:
    def get_model(self):
        return WorkflowFakeLLM()


@pytest.fixture
def workflow_llm_provider():
    return WorkflowFakeLLMProvider()
