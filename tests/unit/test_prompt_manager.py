from __future__ import annotations

from healthbot.services.prompt_manager import PromptManager


def test_prompt_manager_renders_health_agent_v1():
    manager = PromptManager()

    messages = manager.render(
        "health_agent",
        version="v1",
        question="What is diabetes?",
        source_context="No external sources were retrieved.",
    )

    assert messages
    assert any("What is diabetes?" in message.content for message in messages)


def test_prompt_manager_renders_health_agent_v2():
    manager = PromptManager()

    messages = manager.render(
        "health_agent",
        version="v2",
        question="What is diabetes?",
        source_context="No external sources were retrieved.",
    )

    assert messages
    assert any("What is diabetes?" in message.content for message in messages)


def test_prompt_manager_renders_topic_rejection_v1():
    manager = PromptManager()

    messages = manager.render(
        "topic_rejection",
        version="v1",
        question="Write JavaScript code.",
    )

    assert messages
    assert any("Write JavaScript code." in message.content for message in messages)