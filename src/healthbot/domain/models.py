from langgraph.graph.message import MessagesState


# Models representing workflow state.
class WorkflowState(MessagesState):
    """
    State object passed between LangGraph workflow.

    This state contains all data required for the
    health education workflow.
    """

    question: str
    answer: str = ""
    health_topic: bool = True

    quiz_question: str = ""
    quiz_correct_answer: str = ""
    user_quiz_answer: str = ""
    quiz_answer: str = ""

    quiz_generated: bool = False
    quiz_approved: bool = False
    quiz_graded: bool = False
    is_correct: bool = False
    score: int = 0

    research_completed: bool = False
    summary_completed: bool = False

    error: str = ""
    grading_error: str = ""

    explanation_provided: bool = False
    ready_for_quiz: bool = False
    workflow_completed: bool = False
