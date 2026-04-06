from langgraph.graph.message import MessagesState


# Models representing e2e state.
class WorkflowState(MessagesState):
    """
    State object passed between LangGraph e2e.

    This state contains all data required for the
    health education e2e.
    """

    question: str
    health_topic: bool = True
    quiz_question: str = ""
    quiz_correct_answer: str = ""
    user_quiz_answer: str = ""
    quiz_approved: bool = False
    quiz_generated: bool = False
    quiz_graded: bool = False
    is_correct: bool = False
    score: int = 0
