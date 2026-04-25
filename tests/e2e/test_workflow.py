from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from healthbot.workflow.nodes import HealthWorkflowNodes


class FakeQuiz:
    def model_dump(self):
        return {
            "question": "Which organ mainly pumps blood through the body?",
            "option_a": "Liver",
            "option_b": "Heart",
            "option_c": "Kidney",
            "option_d": "Lung",
            "correct_answer": "B",
        }


class FakeExplanation:
    def model_dump(self):
        return {
            "explanation": "The heart pumps blood throughout the body.",
            "key_concepts": "Heart, circulation, oxygen delivery",
            "citations": "Educational summary",
            "learning_tips": "Review the role of the cardiovascular system.",
        }


class FakeStructuredLLM:
    def __init__(self, schema):
        self.schema = schema

    def invoke(self, messages):
        schema_name = getattr(self.schema, "__name__", "")
        if schema_name == "QuizQuestion":
            return FakeQuiz()
        return FakeExplanation()


class FakeLLM:
    def invoke(self, messages):
        return AIMessage(content="Stub response about diabetes.")

    def with_structured_output(self, schema):
        return FakeStructuredLLM(schema)


class FakeLLMProvider:
    def get_model(self):
        return FakeLLM()


def test_entry_point_builds_expected_message_stack():
    nodes = HealthWorkflowNodes(FakeLLMProvider())

    state = {"question": "What is diabetes?"}
    result = nodes.entry_point(state)

    assert "messages" in result
    assert len(result["messages"]) >= 3
    assert any(isinstance(message, SystemMessage) for message in result["messages"])
    assert any(isinstance(message, HumanMessage) for message in result["messages"])


def test_health_agent_returns_ai_message():
    nodes = HealthWorkflowNodes(FakeLLMProvider())

    state = {
        "question": "What is diabetes?",
        "messages": [HumanMessage(content="What is diabetes?")],
    }

    result = nodes.health_agent(state)

    assert "messages" in result
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)
    assert "Stub response" in result["messages"][0].content


def test_quiz_generation_node_builds_multiple_choice_quiz():
    nodes = HealthWorkflowNodes(FakeLLMProvider())

    state = {"messages": [AIMessage(content="The heart is a muscular organ that pumps blood.")]}

    result = nodes.quiz_generation_node(state)

    assert result["quiz_generated"] is True
    assert result["quiz_correct_answer"] == "B"
    assert "A)" in result["quiz_question"]
    assert "B)" in result["quiz_question"]
    assert "Reply with A, B, C, or D." in result["quiz_question"]


def test_quiz_generation_node_handles_missing_summary():
    nodes = HealthWorkflowNodes(FakeLLMProvider())

    result = nodes.quiz_generation_node({"messages": []})

    assert result["quiz_generated"] is False
    assert "couldn't generate a quiz" in result["messages"][0].content.lower()


def test_quiz_grader_node_returns_feedback_payload():
    nodes = HealthWorkflowNodes(FakeLLMProvider())

    state = {
        "messages": [AIMessage(content="The heart pumps blood through the body.")],
        "quiz_question": "Which organ mainly pumps blood through the body?",
        "user_quiz_answer": "B",
        "quiz_correct_answer": "B",
    }

    result = nodes.quiz_grader_node(state)

    assert result["quiz_graded"] is True
    assert result["is_correct"] is True
    assert result["score"] == 100
    assert "Correct!" in result["messages"][0].content
    assert "Explanation:" in result["messages"][0].content
