"""LangGraph Demo 1: Simple heuristic routing for customer feedback.

This demo shows a LangGraph that routes customer feedback to either
a question handler or compliment handler based on a simple heuristic
(presence of '?' character), then beautifies the response.

Integrated from CS5474 Software V&V course - LangGraph Hands-on 1.
"""

from __future__ import annotations

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END


class Demo1State(TypedDict):
    """State for Demo 1 graph."""

    text: str
    answer: str
    payload: list[dict]


def extract_content(state: Demo1State) -> dict:
    """Extract text from payload."""
    return {"text": state["payload"][0]["customer_remark"]}


def route_question_or_compliment(state: Demo1State) -> str:
    """Route based on presence of question mark."""
    return "question" if "?" in state["text"] else "compliment"


def run_compliment_code(state: Demo1State) -> dict:
    """Handle compliment."""
    return {"answer": "Thanks for the compliment."}


def run_question_code(state: Demo1State) -> dict:
    """Handle question."""
    return {"answer": "Thanks for your question. We will look into it."}


def beautify(state: Demo1State) -> dict:
    """Beautify the response."""
    return {"answer": state["answer"] + " (beautified)"}


def build_demo1_graph() -> StateGraph:
    """Build and return the Demo 1 graph."""
    graph_builder = StateGraph(Demo1State)

    graph_builder.add_node("extract_content", extract_content)
    graph_builder.add_node("run_question_code", run_question_code)
    graph_builder.add_node("run_compliment_code", run_compliment_code)
    graph_builder.add_node("beautify", beautify)

    graph_builder.add_edge(START, "extract_content")

    graph_builder.add_conditional_edges(
        "extract_content",
        route_question_or_compliment,
        {
            "compliment": "run_compliment_code",
            "question": "run_question_code",
        },
    )

    graph_builder.add_edge("run_question_code", "beautify")
    graph_builder.add_edge("run_compliment_code", "beautify")
    graph_builder.add_edge("beautify", END)

    return graph_builder.compile()


demo1_graph = build_demo1_graph()


if __name__ == "__main__":
    graph = build_demo1_graph()

    example_payload = [
        {
            "time_of_comment": "2025-01-20",
            "customer_remark": "Why has the packaging changed?",
            "social_media_channel": "facebook",
            "number_of_likes": 100,
        }
    ]

    result = graph.invoke({"payload": example_payload})
    print("\nFINAL RESULT:\n", result)

    print("\nSTEP-BY-STEP STREAM:\n")
    for step in graph.stream({"payload": example_payload}):
        print(step)
