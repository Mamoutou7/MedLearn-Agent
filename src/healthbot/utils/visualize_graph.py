from src.healthbot.workflow.workflow_builder import WorkflowBuilder

if __name__ == "__main__":

    graph = WorkflowBuilder()

    graph.visualize()

    print("Graph visualization generated: healthbot_graph.png")
