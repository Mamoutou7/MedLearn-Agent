"""
Routing logic used by the LangGraph workflow.

Routers determine the next node to execute based
on the current workflow state and messages.

This module keeps routing rules isolated from
business logic to maintain separation of concerns.
"""

from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.graph.message import MessagesState

# GLOBAL VARIABLES
Route = Literal["health_agent", "tools", "quiz_approval"]
ValidationRoute = Literal["continue", "reject"]


class WorkflowRouter:
    """
    Router responsible for determining the next
    node in the LangGraph workflow.
    """

    def route(self, state: MessagesState) -> Route:
        """
        Determine the next workflow step after the health agent.

        Decision logic:
        1. If the LLM triggered tool calls -> go to tools node
        2. If an AI message was produced -> offer quiz
        3. Otherwise -> continue conversation with agent
        """

        last_message = state["messages"][-1]

        # Tool execution requested by LLM
        if self._has_tool_calls(last_message):
            return "tools"

        # AI response ready → propose quiz
        if self._should_propose_quiz(last_message, state):
            return "quiz_approval"

        return "__end__"

    def validation_route(self, state) -> ValidationRoute:
        """
        Determine whether the workflow should continue
        after topic validation.
        """

        return "continue" if state.get("health_topic") else "reject"

    # ---------- Private helpers ----------
    def _has_tool_calls(self, message) -> bool:
        """Check if the LLM requested tool execution."""
        return hasattr(message, "tool_calls") and bool(message.tool_calls)

    def _should_propose_quiz(self, message, state) -> bool:
        """Check if a quiz should be proposed."""
        return isinstance(message, AIMessage) and not state.get("quiz_approved")
