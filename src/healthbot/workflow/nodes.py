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
from healthbot.core.settings import settings
from healthbot.domain.evidence import EvidenceSource
from healthbot.domain.models import WorkflowState
from healthbot.infra.llm_provider import LLMProvider
from healthbot.infra.web_search_tool import web_search_tool
from healthbot.prompts.health_agent import build_welcome_messages
from healthbot.services.answer_composer import AnswerComposer
from healthbot.services.explanation_service import ExplanationService
from healthbot.services.health_validator import HealthValidator
from healthbot.services.medical_policy import MedicalPolicy
from healthbot.services.prompt_manager import PromptManager
from healthbot.services.quiz_service import (
    QuizApprovalService,
    QuizGradingService,
    QuizService,
)
from healthbot.services.safety_classifier import SafetyClassifier
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
        self.prompt_manager = PromptManager()
        self.safety_classifier = SafetyClassifier()
        self.medical_policy = MedicalPolicy()
        self.answer_composer = AnswerComposer()

    # ENTRY POINT
    def entry_point(self, state: WorkflowState) -> dict:
        """
        Entry point of the e2e.
        """
        question = state.get("question", "")

        with tracer.start_as_current_span("workflow.entry_point") as current_span:
            current_span.set_attribute("question.length", len(question))
            logger.info("Starting new HealthBot session")

            return {
                "messages": [
                    *build_welcome_messages(question=question),
                    SystemMessage(content="Answer the user's health question clearly and safely."),
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

    # RETRIEVAL NODE
    def retrieval_node(self, state: WorkflowState) -> dict:
        """Retrieve external evidence for grounded health answers."""
        question = state.get("question", "")

        with tracer.start_as_current_span("workflow.retrieval") as current_span:
            current_span.set_attribute("question.length", len(question))
            logger.info("Retrieving external health evidence")

            if not question.strip():
                current_span.set_attribute("retrieval.skipped", True)
                return {
                    "sources": [],
                    "source_query": question,
                    "grounding_used": False,
                }

            try:
                result = web_search_tool.invoke(question)

                sources = result.get("results", [])
                current_span.set_attribute("retrieval.source_count", len(sources))
                current_span.set_attribute(
                    "retrieval.trusted_source_count",
                    sum(1 for source in sources if source.get("trusted_source")),
                )

                return {
                    "sources": sources,
                    "source_query": result.get("query", question),
                    "grounding_used": bool(sources),
                }

            except Exception as exc:
                current_span.record_exception(exc)
                current_span.set_attribute("error", True)
                logger.exception("Retrieval failed; continuing without sources")

                return {
                    "sources": [],
                    "source_query": question,
                    "grounding_used": False,
                }

    # AGENT NODE
    def health_agent(self, state: WorkflowState) -> dict:
        """
        Main LLM agent node.
        """
        question = state.get("question", "")
        history = state.get("messages", [])

        sources = state.get("sources", [])
        source_context = self._format_sources_for_prompt(sources)

        logger.info("Running health agent")

        with tracer.start_as_current_span("workflow.health_agent") as current_span:
            current_span.set_attribute("question.length", len(question))
            current_span.set_attribute("history.count", len(history))

            classification = self.safety_classifier.classify(question)
            current_span.set_attribute("safety.category", classification.category)
            current_span.set_attribute("safety.severity", classification.severity)
            current_span.set_attribute(
                "safety.should_short_circuit",
                classification.should_short_circuit,
            )

            if classification.matched_rules:
                current_span.set_attribute(
                    "safety.matched_rules",
                    ",".join(classification.matched_rules),
                )

            if classification.should_short_circuit:
                logger.warning(
                    "Safety classifier short-circuited LLM call | category=%s | severity=%s",
                    classification.category,
                    classification.severity,
                )
                current_span.set_attribute("llm.skipped", True)

                return {
                    "messages": [
                        AIMessage(
                            content=classification.message
                            or (
                                "This may require urgent medical attention. "
                                "Please contact emergency services or a qualified healthcare \
                                professional."
                            )
                        )
                    ],
                    "answer": classification.message,
                    "safety_short_circuit": True,
                    "safety_category": classification.category,
                    "safety_severity": classification.severity,
                }

            try:
                prompt_messages = self.prompt_manager.render(
                    "health_agent",
                    version=settings.health_agent_prompt_version,
                    question=question,
                    source_context=source_context,
                )
                current_span.set_attribute("prompt.message_count", len(prompt_messages))

                if history:
                    injected_history = history[-4:]
                    messages = prompt_messages[:-1] + injected_history + [prompt_messages[-1]]
                    current_span.set_attribute("history.injected_count", len(injected_history))
                else:
                    messages = prompt_messages
                    current_span.set_attribute("history.injected_count", 0)

                response = self.llm.invoke(
                    messages,
                    span_name="llm.health_agent",
                )

                response = self.safety_service.apply(response, question=question)
                response = self.medical_policy.enforce_on_message(response)

                evidence_sources = [
                    EvidenceSource(
                        title=item.get("title", "Untitled source"),
                        url=item.get("url", ""),
                        domain=item.get("domain", ""),
                        content=item.get("content", ""),
                        trusted_source=bool(item.get("trusted_source", False)),
                        score=item.get("score"),
                    )
                    for item in sources
                ]

                content = getattr(response, "content", "")
                if isinstance(content, str) and evidence_sources:
                    current_span.set_attribute("response.length", len(content))

                    response = AIMessage(
                        content=self.answer_composer.compose(
                            content,
                            sources=evidence_sources,
                            include_disclaimer=False,
                        ),
                        additional_kwargs=response.additional_kwargs,
                        response_metadata=response.response_metadata,
                    )

                return {"messages": [response]}

            except Exception as exc:
                current_span.record_exception(exc)
                current_span.set_attribute("error", True)
                logger.exception("LLM execution failed")
                raise LLMServiceError("Agent execution failed") from exc

    def _format_sources_for_prompt(self, sources: list[dict]) -> str:
        if not sources:
            return "No external sources were retrieved."

        lines = []
        for idx, source in enumerate(sources, start=1):
            title = source.get("title") or "Untitled source"
            domain = source.get("domain") or "unknown source"
            content = source.get("content") or ""
            url = source.get("url") or ""

            lines.append(
                "\n".join(
                    [
                        f"[{idx}] {title}",
                        f"Domain: {domain}",
                        f"URL: {url}",
                        f"Content: {content}",
                    ]
                )
            )

        return "\n\n".join(lines)

    # REJECTION NODE
    def rejection_node(self, state: WorkflowState):
        """Reject non-health questions using the central prompt registry."""
        question = state.get("question", "")

        with tracer.start_as_current_span("workflow.rejection_node") as current_span:
            current_span.set_attribute("question.length", len(question))
            logger.info("Rejecting non-health question")

            try:
                rejection_messages = self.prompt_manager.render(
                    "topic_rejection",
                    version=settings.topic_rejection_prompt_version,
                    question=question,
                )
                current_span.set_attribute("prompt.message_count", len(rejection_messages))

                rejection_response = self.llm.invoke(
                    rejection_messages,
                    span_name="llm.rejection",
                )
                rejection_message = rejection_response.content

                if isinstance(rejection_message, str):
                    current_span.set_attribute("response.length", len(rejection_message))

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
                    {quiz["question"]}
            
                    A) {quiz["option_a"]}
                    B) {quiz["option_b"]}
                    C) {quiz["option_c"]}
                    D) {quiz["option_d"]}
            
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
