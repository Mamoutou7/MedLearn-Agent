"""
This module is responsible for constructing and compiling
the LangGraph workflow used by the HealthBot application.

Responsibilities
----------------
- Register workflow nodes
- Define routing logic
- Configure graph transitions
- Compile the LangGraph state machine
"""

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from healthbot.core.logging import get_logger
from healthbot.infra.llm_provider import LLMProvider
from healthbot.domain.models import WorkflowState
from healthbot.infra.web_search_tool import web_search_tool
from healthbot.workflow.nodes import HealthWorkflowNodes
from healthbot.workflow.router import WorkflowRouter
from healthbot.infra.checkpointing.factory import CheckpointerHandle, build_checkpointer
from healthbot.core.settings import Settings, get_settings



logger = get_logger(__name__)


class WorkflowBuilder:
    """
    Responsible for constructing the LangGraph workflow.

    This class encapsulates all graph creation logic to ensure
    a clean separation between workflow orchestration and
    application logic.
    """

    def __init__(self, settings: Settings | None = None):
        """Initialize the workflow builder."""
        self.settings = settings or get_settings()
        self.checkpointer_handle: CheckpointerHandle = build_checkpointer(self.settings)
        self.nodes = HealthWorkflowNodes(LLMProvider())
        self.router = WorkflowRouter()

    def build(self):
        """
        Build and compile the HealthBot workflow graph.

        Returns
        -------
        CompiledStateGraph
            Executable LangGraph workflow.
        """

        logger.info("Building HealthBot workflow")

        workflow = StateGraph(WorkflowState)

        # Register Nodes
        workflow.add_node("entry_point", self.nodes.entry_point)
        workflow.add_node("health_validation", self.nodes.health_validation_node)
        workflow.add_node("health_agent", self.nodes.health_agent)
        workflow.add_node("tools", ToolNode([web_search_tool]))
        workflow.add_node("rejection", self.nodes.rejection_node)
        workflow.add_node("quiz_approval", self.nodes.quiz_approval_node)
        workflow.add_node("quiz_generation", self.nodes.quiz_generation_node)
        workflow.add_node("quiz_answer_collection", self.nodes.quiz_answer_node)
        workflow.add_node("quiz_grader", self.nodes.quiz_grader_node)

        # Entry Point
        workflow.set_entry_point("entry_point")

        # Core Flow
        workflow.add_edge("entry_point", "health_validation")

        # Validation router
        workflow.add_conditional_edges(
            source="health_validation",
            path=self.router.validation_route,
            path_map={
                "continue": "health_agent",
                "reject": "rejection",
            },
        )

        # Agent router
        workflow.add_conditional_edges(
            source="health_agent",
            path=self.router.route,
            path_map={
                "tools": "tools",
                "quiz_approval": "quiz_approval",
                "__end__": END,
            },
        )

        workflow.add_edge("tools", "health_agent")
        # Quiz Workflow
        workflow.add_edge("quiz_generation", "quiz_answer_collection")
        workflow.add_edge("quiz_grader", "end_workflow")
        # Rejection Flow
        workflow.add_edge("rejection", "end_workflow")
        # End Workflow Node
        workflow.add_node("end_workflow", self.nodes.end_workflow_node)
        workflow.add_edge("end_workflow", END)

        # Compile Graph
        logger.info("Compiling HealthBot workflow")

        graph = workflow.compile(checkpointer=self.checkpointer_handle.resource)

        logger.info("Workflow successfully compiled")

        return graph

    # GRAPH VISUALIZATION
    def visualize(self):
        """
        Generate a PNG visualization of the LangGraph workflow.
        """
        graph = self.build()
        graph_png = graph.get_graph().draw_mermaid_png()

        with open("healthbot_graph.png", "wb") as f:
            f.write(graph_png)

    def close(self) -> None:
        self.checkpointer_handle.close()