"""
Workflow nodes used by the LangGraph state machine.
"""

from textwrap import dedent
from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import Command, interrupt
from opentelemetry import trace

from healthbot.core.exceptions import LLMServiceError
from healthbot.core.logging import get_logger
from healthbot.domain.models import WorkflowState
from healthbot.infra.llm_provider import LLMProvider
from healthbot.prompts.health_agent import (
    build_health_agent_messages,
    build_welcome_messages,
)
from healthbot.prompts.rejection import build_rejection_messages
from healthbot.services.explanation_service import ExplanationService
from healthbot.services.health_validator import HealthValidator
from healthbot.services.quiz_service import (
    QuizApprovalService,
    QuizGradingService,
    QuizService,
)
from healthbot.services.safety_service import SafetyService

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)

class HealthWorkflowNodes:
    """
    Collection of e2e nodes used in the LangGraph state machine.
    Each node is a method of this class.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.llm = llm_provider.get_model()
        self.validator = HealthValidator(llm_provider)
        self.quiz_service = QuizService(llm_provider)
        self.grading_service = QuizGradingService()
        self.explanation_service = ExplanationService(llm_provider)
        self.approval_service = QuizApprovalService()
        self.safety_service = SafetyService()

    # ENTRY POINT
    def entry_point(self, state: WorkflowState) -> dict:
        """
        Entry point of the e2e.
        """
        question = state.get("question", "")

        with tracer.start_as_current_span(
                "workflow.entry_point"
        ) as current_span:
            current_span.set_attribute("question.length", len(question))
            logger.info("Starting new HealthBot session")

            return {
                "messages": [
                    *build_welcome_messages(question=question),
                    SystemMessage(
                        content="Answer the user's health question clearly and safely."
                    ),
                    HumanMessage(content=question),
                ]
            }

    # VALIDATION NODE
    def health_validation_node(self, state: WorkflowState) -> dict:
        """
        Validate health question.
        """

        question = state.get("question", "")

        with tracer.start_as_current_span("workflow.health_validation") as current_span:
            current_span.set_attribute("question.length", len(question))
            logger.info("Validating health question")

            try:
                result = self.validator.validate(question)
                health_topic = bool(result.get("health_topic", False))
                current_span.set_attribute("health_topic", health_topic)
                return result

            except Exception as exc:
                current_span.record_exception(exc)
                current_span.set_attribute("error", True)
                logger.exception("Health validation failed")

                raise LLMServiceError(
                    "Health validation failed",
                    context={"question": question},
                ) from exc

    # AGENT NODE
    def health_agent(self, state: WorkflowState) -> dict:
        """
        Main LLM agent node.
        """
        question = state.get("question", "")
        history = state.get("messages", [])

        logger.info("Running health agent")

        with tracer.start_as_current_span("workflow.health_agent") as current_span:
            current_span.set_attribute("question.length", len(question))
            current_span.set_attribute("history.count", len(history))

            try:
                prompt_messages = build_health_agent_messages(question=question)

                if history:
                    messages = prompt_messages[:-1] + history[-4:] + [prompt_messages[-1]]
                else:
                    messages = prompt_messages
                response = self.llm.invoke(messages)
                return {"messages": [response]}

            except Exception as exc:
                current_span.record_exception(exc)
                current_span.set_attribute("error", True)
                logger.exception("LLM execution failed")
                raise LLMServiceError("Agent execution failed") from exc

    # REJECTION NODE
    def rejection_node(self, state: WorkflowState):
        """Reject non-health questions using the central prompt registry."""
        question = state.get("question", "")

        with tracer.start_as_current_span("workflow.rejection_node") as current_span:
            current_span.set_attribute("question.length", len(question))
            logger.info("Rejecting non-health question")

            try:
                rejection_messages = build_rejection_messages(question=question)
                current_span.set_attribute("prompt.message_count", len(rejection_messages))

                rejection_message = self.llm.invoke(rejection_messages).content
                if isinstance(rejection_message, str):
                    current_span.set_attribute("response.message", len(rejection_message))

                return {
                    "messages": [AIMessage(content=rejection_message)],
                    "answer": rejection_message,
                    "question": question,
                    "health_topic": False,
                }

            except Exception as exc:
                current_span.record_exception(exc)
                current_span.set_attribute("error", True)
                logger.exception("Rejection node failed")

                raise LLMServiceError("Rejection node failed") from exc

    # QUIZ GENERATION
    def quiz_generation_node(self, state: WorkflowState):
        """
        LangGraph node responsible for generating a quiz question
        based on the health summary produced by the agent.

        This node extracts the latest AI-generated health explanation
        from the conversation history and delegates quiz generation
        to the QuizService.

        Parameters
        ----------
        state : WorkflowState
            Current e2e state containing the conversation history.

        Returns
        -------
        dict
            Updated state containing the generated quiz question
            and the correct answer.
        """
        with tracer.start_as_current_span("workflow.quiz_generation") as current_span:
            logger.info("Generating quiz question")

            messages = state.get("messages", [])
            current_span.set_attribute("history.count", len(messages))

            summary = ""
            # Extract the latest AI explanation (summary)
            for message in reversed(messages):
                if isinstance(message, AIMessage) and message.content:
                    summary = message.content
                    break

            current_span.set_attribute("summary.found", bool(summary))
            current_span.set_attribute("summary.length", len(summary))

            if not summary:
                logger.warning("No summary found for quiz generation")
                return {
                    "messages": [
                        AIMessage(
                            content="Sorry, I couldn't generate "
                                    "a quiz because no health summary was found."
                        )
                    ],
                    "quiz_generated": False,
                }

            try:
                quiz = self.quiz_service.generate_quiz(summary)

                quiz_text = dedent(f"""        
                    {quiz['question']}
            
                    A) {quiz['option_a']}
                    B) {quiz['option_b']}
                    C) {quiz['option_c']}
                    D) {quiz['option_d']}
            
                    Reply with A, B, C, or D.
                """).strip()

                logger.info("Quiz generated successfully")

                return {
                    "messages": [AIMessage(content=quiz_text)],
                    "quiz_generated": True,
                    "quiz_question": quiz_text,
                    "quiz_correct_answer": quiz["correct_answer"],
                }

            except Exception as exc:
                current_span.record_exception(exc)
                current_span.set_attribute("error", True)
                logger.exception("Quiz generation failed")
                raise LLMServiceError(
                    "Quiz generation failed",
                    context={"summary": summary[:200]},
                ) from exc

    def quiz_approval_node(
        self, state: WorkflowState
    ) -> Command[Literal["quiz_generation", "end_workflow"]]:
        """
        Node asking the user if they want a quiz.

        This node interrupts the e2e and waits for
        user input before continuing.

        Parameters
        ----------
        state : WorkflowState

        Returns
        -------
        Command
        """

        with tracer.start_as_current_span("workflow.quiz_approval") as current_span:
            logger.info("Requesting quiz approval")

            summary = ""
            for message in reversed(state["messages"]):
                if hasattr(message, "content"):
                    summary = message.content
                    break

            current_span.set_attribute("summary.length", len(summary))
            decision = interrupt(
                {
                    "question": "Would you like a short quiz?",
                    "full_summary": summary,
                }
            )

            approved = self.approval_service.approve(decision)
            current_span.set_attribute("quiz.approved", approved)

            if approved:
                logger.info("Quiz approved by user")

                return Command(
                    goto="quiz_generation",
                    update={"quiz_approved": True},
                )
            logger.info("Quiz rejected by user")
            return Command(goto="end_workflow")

    def quiz_answer_node(
        self, state: WorkflowState
    ) -> Command[Literal["quiz_grader", "end_workflow"]]:
        """
        Node responsible for collecting the user's quiz answer.

        This node interrupts the e2e and waits for the
        user to submit an answer.

        Parameters
        ----------
        state : WorkflowState

        Returns
        -------
        Command
        """
        with tracer.start_as_current_span("workflow.quiz_answer") as current_span:
            logger.info("Waiting for user quiz answer")

            quiz_question = state.get("quiz_question", "")
            current_span.set_attribute("quiz_question.length", len(quiz_question))

            answer = interrupt({"quiz_question": state["quiz_question"]})
            answer = str(answer).upper().strip()

            current_span.set_attribute("quiz.answer", answer)

            if not self.grading_service.validate_answer(answer):
                logger.warning("Invalid quiz answer received")

                return Command(goto="end_workflow")
            return Command(
                goto="quiz_grader",
                update={"user_quiz_answer": answer},
            )

    def quiz_grader_node(self, state: WorkflowState):
        """
        Node responsible for grading the quiz and generating
        a detailed explanation.

        Parameters
        ----------
        state : WorkflowState

        Returns
        -------
        dict
        """
        with tracer.start_as_current_span("workflow.quiz_grader") as current_span:
            logger.info("Grading quiz answer")

            user_answer = state.get("user_quiz_answer")
            correct_answer = state.get("quiz_correct_answer")

            current_span.set_attribute("quiz.user_answer", str(user_answer))
            current_span.set_attribute("quiz.correct_answer", str(correct_answer))

            try:
                grading_result = self.grading_service.grade(
                    user_answer,
                    correct_answer,
                )

                is_correct = grading_result["is_correct"]
                score = grading_result["score"]

                current_span.set_attribute("quiz.is_correct", bool(is_correct))
                current_span.set_attribute("quiz.score", int(score))

                summary = ""
                for message in reversed(state["messages"]):
                    if hasattr(message, "content"):
                        summary = message.content
                        break

                explanation = self.explanation_service.generate_explanation(
                    quiz_question=state.get("quiz_question"),
                    user_answer=user_answer,
                    correct_answer=correct_answer,
                    is_correct=is_correct,
                    summary=summary,
                )

                if is_correct:
                    header = dedent(
                        f"""
                        🎉 Correct!
                        Your answer {user_answer} is correct.
                        Score: {score}%
                        """
                    ).strip()
                else:
                    header = dedent(
                        f"""
                        📚 Learning opportunity
                        Your answer {user_answer} is incorrect.
                        Correct answer: {correct_answer}
                        Score: {score}%
                        """
                    ).strip()

                feedback = dedent(
                    f"""
                    {header}
                    Explanation:
                    {explanation["explanation"]}
            
                    Key Concepts:
                    {explanation["key_concepts"]}
            
                    Supporting Information:
                    {explanation["citations"]}
            
                    Learning Tips:
                    {explanation["learning_tips"]}
                    """
                ).strip()

                current_span.set_attribute("feedback.length", len(feedback))

                return {
                    "messages": [AIMessage(content=feedback)],
                    "quiz_graded": True,
                    "is_correct": is_correct,
                    "score": score,
                }

            except Exception as exc:
                current_span.record_exception(exc)
                current_span.set_attribute("error", True)
                logger.exception("Quiz grading failed")
                raise LLMServiceError("Quiz grading failed") from exc

    # END WORKFLOW
    def end_workflow_node(self, state: WorkflowState) -> dict:
        """Return the final closing message."""
        with tracer.start_as_current_span("workflow.end") as current_span:
            message = "Thanks for using HealthBot!"
            current_span.set_attribute("response.length", len(message))
            return {"messages": [AIMessage(content=message)]}