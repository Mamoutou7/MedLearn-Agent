from healthbot.workflow.nodes import HealthWorkflowNodes
from healthbot.infra.llm_provider import LLMProvider


def test_entry_point():
    """
    Entry point should add system + user message.
    """

    nodes = HealthWorkflowNodes(LLMProvider())

    state = {"question": "What is diabetes?"}

    result = nodes.entry_point(state)

    assert "messages" in result
    assert len(result["messages"]) == 2


def test_health_validation_node_valid(monkeypatch):
    """
    Should allow health questions.
    """

    nodes = HealthWorkflowNodes(LLMProvider())

    fake_result = {
        "health_topic": True,
        "question": "What is diabetes?",
        "messages": [],
    }

    monkeypatch.setattr(nodes.validator, "validate", lambda q: fake_result)

    state = {"question": "What is diabetes?"}

    result = nodes.health_validation_node(state)

    assert result["health_topic"] is True


def test_rejection_node():
    """
    Non-health questions should be rejected.
    """

    nodes = HealthWorkflowNodes(LLMProvider())

    state = {"question": "Who won the World Cup?"}

    result = nodes.rejection_node(state)

    assert result["health_topic"] is False
    assert "health related topics" in result["answer"]