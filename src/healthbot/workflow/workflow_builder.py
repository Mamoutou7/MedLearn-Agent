from langgraph.graph import END, StateGraph

from healthbot.core.logging import get_logger
from healthbot.core.settings import Settings, get_settings
from healthbot.domain.models import WorkflowState
from healthbot.infra.checkpointing.factory import CheckpointerHandle, build_checkpointer
from healthbot.infra.llm_provider import LLMProvider
from healthbot.workflow.nodes import HealthWorkflowNodes
from healthbot.workflow.router import WorkflowRouter

logger = get_logger(__name__)


class WorkflowBuilder:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.checkpointer_handle: CheckpointerHandle = build_checkpointer(self.settings)
        self.nodes = HealthWorkflowNodes(LLMProvider())
        self.router = WorkflowRouter()

    def build(self):
        logger.info("Building HealthBot e2e")

        workflow = StateGraph(WorkflowState)

        workflow.add_node("entry_point", self.nodes.entry_point)
        workflow.add_node("health_validation", self.nodes.health_validation_node)
        workflow.add_node("retrieval", self.nodes.retrieval_node)
        workflow.add_node("health_agent", self.nodes.health_agent)
        workflow.add_node("rejection", self.nodes.rejection_node)
        workflow.add_node("quiz_approval", self.nodes.quiz_approval_node)
        workflow.add_node("quiz_generation", self.nodes.quiz_generation_node)
        workflow.add_node("quiz_answer_collection", self.nodes.quiz_answer_node)
        workflow.add_node("quiz_grader", self.nodes.quiz_grader_node)
        workflow.add_node("end_workflow", self.nodes.end_workflow_node)

        workflow.set_entry_point("entry_point")

        workflow.add_edge("entry_point", "health_validation")

        workflow.add_conditional_edges(
            source="health_validation",
            path=self.router.validation_route,
            path_map={
                "continue": "retrieval",
                "reject": "rejection",
            },
        )

        workflow.add_edge("retrieval", "health_agent")

        workflow.add_conditional_edges(
            source="health_agent",
            path=self.router.route,
            path_map={
                "quiz_approval": "quiz_approval",
                "__end__": END,
            },
        )

        workflow.add_edge("quiz_generation", "quiz_answer_collection")
        workflow.add_edge("quiz_grader", "end_workflow")
        workflow.add_edge("rejection", "end_workflow")
        workflow.add_edge("end_workflow", END)

        logger.info("Compiling HealthBot e2e")
        graph = workflow.compile(checkpointer=self.checkpointer_handle.resource)
        logger.info("Workflow successfully compiled")

        return graph

    def visualize(self):
        graph = self.build()
        graph_png = graph.get_graph().draw_mermaid_png()

        with open("healthbot_graph.png", "wb") as f:
            f.write(graph_png)

    def close(self) -> None:
        self.checkpointer_handle.close()