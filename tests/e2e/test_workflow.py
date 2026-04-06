from langchain_core.messages import AIMessage

from healthbot.workflow.nodes import HealthWorkflowNodes


class FakeLLM:
    def invoke(self, messages):
        return AIMessage(content="Stub response")


class FakeLLMProvider:
    def get_model(self):
        return FakeLLM()


def test_entry_point():
    nodes = HealthWorkflowNodes(FakeLLMProvider())
    state = {"question": "What is diabetes?"}
    result = nodes.entry_point(state)
    assert "messages" in result
    assert len(result["messages"]) >= 2