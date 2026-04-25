import warnings

from langgraph.types import Command

from healthbot.utils.get_interrupt_value import get_interrupt_value
from healthbot.workflow.workflow_builder import WorkflowBuilder

warnings.filterwarnings("ignore", category=UserWarning)


def run_session(graph, question, thread_id):
    """
    Execute one HealthBot session.
    """

    config = {"configurable": {"thread_id": thread_id}}

    result = graph.invoke({"question": question}, config=config)

    # If no interrupt, just display the result
    if "__interrupt__" not in result:
        if result.get("messages"):
            print("HEALTHBOT RESPONSE")
            result["messages"][-1].pretty_print()
        return

    interrupt_data = result["__interrupt__"]

    summary = get_interrupt_value(interrupt_data, "full_summary")

    print("HEALTH SUMMARY")

    print(summary)

    decision = (
        input("\nWould you like to test your knowledge with a quiz? (approve/reject): ")
        .strip()
        .lower()
    )

    if decision not in ["approve", "yes", "y"]:
        print("\nQuiz skipped.")
        graph.invoke(Command(resume="reject"), config=config)
        return

    result = graph.invoke(Command(resume="approve"), config=config)

    if "__interrupt__" not in result:
        return

    interrupt_data = result["__interrupt__"]

    quiz = get_interrupt_value(interrupt_data, "quiz_question")

    print(quiz)

    answer = input("\nYour answer: ").strip().upper()

    if answer not in ["A", "B", "C", "D"]:
        print("\nInvalid answer. Ending session.")
        return

    print("\nGrading your answer...")

    final_result = graph.invoke(Command(resume=answer), config=config)

    messages = final_result.get("messages", [])
    if len(messages) >= 2:
        print("QUIZ RESULT")
        messages[-2].pretty_print()

    messages[-1].pretty_print()

    print("\nSession completed.")


def human_in_the_loop():
    """
    CLI entrypoint.
    """

    builder = WorkflowBuilder()
    graph = builder.build()

    print("WELCOME TO HEALTHBOT")

    thread_id = 1

    while True:
        question = input(
            "\nWhat health topic would you like to learn about? (or type 'exit'): "
        ).strip()

        if question.lower() in ["exit", "quit"]:
            print("\nThank you for using HealthBot. Stay healthy!")
            break

        run_session(graph, question, thread_id)

        thread_id += 1
