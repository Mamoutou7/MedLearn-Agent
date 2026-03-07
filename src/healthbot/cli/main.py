import sys
from langgraph.types import Command

from src.healthbot.workflow.workflow_builder import WorkflowBuilder
from src.healthbot.utils.interrupts import get_interrupt_value


def run():
    """
    Run HealthBot from the command line.
    """

    graph = WorkflowBuilder.build()

    print("🩺 Welcome to HealthBot!")
    question = input("What health topic would you like to learn about? ")

    config = {"configurable": {"thread_id": 1}}

    result = graph.invoke({"question": question}, config=config)

    if "__interrupt__" in result:

        interrupt_data = result["__interrupt__"]

        summary = get_interrupt_value(interrupt_data, "full_summary")

        print("\n📚 SUMMARY")
        print(summary)

        decision = input("\nWould you like a quiz? (approve/reject): ").strip().lower()

        if decision == "approve":

            result = graph.invoke(Command(resume="approve"), config=config)

            if "__interrupt__" in result:

                interrupt_data = result["__interrupt__"]

                quiz = get_interrupt_value(interrupt_data, "quiz_question")

                print("\n📝 QUIZ")
                print(quiz)

                answer = input("\nYour answer (A/B/C/D): ").strip().upper()

                final = graph.invoke(Command(resume=answer), config=config)

                if final.get("messages"):
                    final["messages"][-1].pretty_print()

        else:
            graph.invoke(Command(resume="reject"), config=config)

    else:
        if result.get("messages"):
            result["messages"][-1].pretty_print()