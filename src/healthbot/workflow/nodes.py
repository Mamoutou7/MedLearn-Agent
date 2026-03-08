"""
Workflow nodes used by the LangGraph state machine.
"""

from typing import Dict, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import Command, interrupt

from src.healthbot.core.exceptions import LLMServiceError
from src.healthbot.core.logging import get_logger
from src.healthbot.domain.models import WorkflowState
from src.healthbot.infra.llm_provider import LLMProvider
from src.healthbot.prompts.health_agent import (
    build_health_agent_messages,
    build_welcome_messages,
)
from src.healthbot.services.explanation_service import ExplanationService
from src.healthbot.services.health_validator import HealthValidator
from src.healthbot.services.quiz_service import (
    QuizApprovalService,
    QuizGradingService,
    QuizService,
)


logger = get_logger(__name__)


class HealthWorkflowNodes:
    """
    Collection of workflow nodes used in the LangGraph state machine.
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

    # ENTRY POINT
    def entry_point(self, state: WorkflowState) -> Dict:
        """
        Entry point of the workflow.
        """
        question = state.get("question", "")
        logger.info("Starting new HealthBot session")

        return {
            "messages": [
                *build_welcome_messages(question=question),
                SystemMessage(content="Answer the user's health question clearly and safely."),
                HumanMessage(content=question),
            ]
        }

    # VALIDATION NODE
    def health_validation_node(self, state: WorkflowState) -> Dict:
        """
        Validate health question.
        """

        question = state.get("question", "")

        logger.info("Validating health question")

        try:
            result = self.validator.validate(question)
            return result

        except Exception as exc:
            logger.exception("Health validation failed")

            raise LLMServiceError(
                "Health validation failed",
                context={"question": question},
            ) from exc

    # AGENT NODE
    def health_agent(self, state: WorkflowState) -> Dict:
        """
        Main LLM agent node.
        """

        question = state.get("question", "")
        history = state.get("messages", [])

        logger.info("Running health agent")

        try:
            prompt_messages = build_health_agent_messages(question=question)

            if history:
                messages = prompt_messages[:-1] + history[-4:] + [prompt_messages[-1]]
            else:
                messages = prompt_messages
            response = self.llm.invoke(messages)
            return {"messages": [response]}

        except Exception as exc:
            logger.exception("LLM execution failed")

            raise LLMServiceError("Agent execution failed") from exc

    # REJECTION NODE
    def rejection_node(self, state: WorkflowState):
        """
        Reject non-health questions.
        """

        question = state.get("question", "")

        logger.info("Rejecting non-health question")

        rejection_message = f"""
            I'm sorry — I can only help with **health related topics**.
            
            Your question: {question}
            I'm specifically designed to help with health-related topics such as:
            - Medical Conditions & Diseases
            - Health Symptoms & Concerns
            - Nutrition & Wellness
            - Exercise & Fitness
            - Mental Health & Wellness
            - Preventive Care & Screenings
            - Medical Procedures & Treatments
    
            Please ask me about any of these health topics or medical conditions instead. 
            I'm here to support your health education journey and provide accurate, helpful information about your health!
        """

        return {
            "messages": [AIMessage(content=rejection_message)],
            "answer": rejection_message,
            "question": question,
            "health_topic": False,
        }

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
            Current workflow state containing the conversation history.

        Returns
        -------
        dict
            Updated state containing the generated quiz question
            and the correct answer.
        """

        logger.info("Generating quiz question")

        messages = state.get("messages", [])

        summary = ""

        # Extract the latest AI explanation (summary)
        for message in reversed(messages):
            if isinstance(message, AIMessage) and message.content:
                summary = message.content
                break

        if not summary:
            logger.warning("No summary found for quiz generation")

            return {
                "messages": [
                    AIMessage(
                        content="Sorry, I couldn't generate a quiz because no health summary was found."
                    )
                ],
                "quiz_generated": False,
            }

        try:
            quiz = self.quiz_service.generate_quiz(summary)

            quiz_text = f"""        
                {quiz['question']}
        
                A) {quiz['option_a']}
                B) {quiz['option_b']}
                C) {quiz['option_c']}
                D) {quiz['option_d']}
        
                Reply with A, B, C, or D.
            """

            logger.info("Quiz generated successfully")

            return {
                "messages": [AIMessage(content=quiz_text)],
                "quiz_generated": True,
                "quiz_question": quiz_text,
                "quiz_correct_answer": quiz["correct_answer"],
            }

        except Exception as exc:
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

        This node interrupts the workflow and waits for
        user input before continuing.

        Parameters
        ----------
        state : WorkflowState

        Returns
        -------
        Command
        """

        logger.info("Requesting quiz approval")

        summary = ""
        for message in reversed(state["messages"]):
            if hasattr(message, "content"):
                summary = message.content
                break

        decision = interrupt(
            {
                "question": "Would you like a short quiz?",
                "full_summary": summary,
            }
        )

        if self.approval_service.approve(decision):
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

        This node interrupts the workflow and waits for the
        user to submit an answer.

        Parameters
        ----------
        state : WorkflowState

        Returns
        -------
        Command
        """

        logger.info("Waiting for user quiz answer")

        answer = interrupt({"quiz_question": state["quiz_question"]})

        answer = str(answer).upper().strip()

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
        logger.info("Grading quiz answer")

        user_answer = state.get("user_quiz_answer")
        correct_answer = state.get("quiz_correct_answer")

        grading_result = self.grading_service.grade(
            user_answer,
            correct_answer,
        )

        is_correct = grading_result["is_correct"]
        score = grading_result["score"]

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
            header = f"""
                🎉 Correct!
                Your answer {user_answer} is correct.
                Score: {score}%
            """

        else:
            header = f"""
                📚 Learning opportunity
                Your answer {user_answer} is incorrect.
                Correct answer: {correct_answer}
                Score: {score}%
            """

        feedback = f"""
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

        return {
            "messages": [AIMessage(content=feedback)],
            "quiz_graded": True,
            "is_correct": is_correct,
            "score": score,
        }

    # END WORKFLOW
    def end_workflow_node(self, state: WorkflowState):
        return {"messages": [AIMessage(content="Thanks for using HealthBot!")]}
