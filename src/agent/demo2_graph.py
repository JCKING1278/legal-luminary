"""LangGraph Demo 2: LLM-based routing for customer feedback.

This demo shows a LangGraph that uses an LLM (Ollama) to classify
customer feedback as either a question or compliment, then processes
and beautifies the response.

Integrated from CS5474 Software V&V course - LangGraph Hands-on 2.
"""

from __future__ import annotations

import json
from typing_extensions import TypedDict, Literal

from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama


Route = Literal["question", "compliment"]


class Demo2State(TypedDict):
    """State for Demo 2 graph."""

    payload: list[dict]
    text: str
    route: Route
    answer: str


def extract_content(state: Demo2State) -> dict:
    """Extract text from payload."""
    return {"text": state["payload"][0]["customer_remark"]}


def llm_route(state: Demo2State) -> dict:
    """Use LLM to classify customer remark as question or compliment."""
    llm = ChatOllama(model="granite-code:20b", temperature=0)

    system = (
        "You are a strict text classifier.\n"
        'Return ONLY valid JSON with exactly one key: "route".\n'
        'The value must be either "question" or "compliment".\n'
        "No extra keys, no explanation, no markdown."
    )
    user = (
        f'Text: "{state["text"]}"\n\n'
        "Classify the text as either:\n"
        '- "question": asks for information, includes inquiries, confusion, requests.\n'
        '- "compliment": praise, appreciation, positive feedback.\n\n'
        "Return JSON now."
    )

    raw = llm.invoke([("system", system), ("user", user)]).content.strip()

    try:
        obj = json.loads(raw)
        route = obj.get("route", "").strip().lower()
    except Exception:
        route = raw.lower()

    if "question" in route:
        return {"route": "question"}
    if "compliment" in route:
        return {"route": "compliment"}

    return {"route": "question"}


def route_from_state(state: Demo2State) -> Route:
    """Return the route from state."""
    return state["route"]


def run_compliment_code(state: Demo2State) -> dict:
    """Handle compliment."""
    return {"answer": "Thanks for the compliment."}


def run_question_code(state: Demo2State) -> dict:
    """Handle question."""
    return {"answer": "Thanks for your question. We will look into it."}


def beautify_llm(state: Demo2State) -> dict:
    """Beautify response using LLM."""
    llm = ChatOllama(model="granite-code:20b", temperature=0)

    prompt = (
        "Rewrite the following customer-service reply politely in ONE short sentence.\n"
        "Do not add new facts.\n\n"
        f"Reply: {state['answer']}"
    )

    pretty = llm.invoke(prompt).content.strip()
    return {"answer": pretty}


def build_demo2_graph() -> StateGraph:
    """Build and return the Demo 2 graph."""
    graph_builder = StateGraph(Demo2State)

    graph_builder.add_node("extract_content", extract_content)
    graph_builder.add_node("llm_route", llm_route)
    graph_builder.add_node("run_question_code", run_question_code)
    graph_builder.add_node("run_compliment_code", run_compliment_code)
    graph_builder.add_node("beautify_llm", beautify_llm)

    graph_builder.add_edge(START, "extract_content")
    graph_builder.add_edge("extract_content", "llm_route")

    graph_builder.add_conditional_edges(
        "llm_route",
        route_from_state,
        {
            "compliment": "run_compliment_code",
            "question": "run_question_code",
        },
    )

    graph_builder.add_edge("run_question_code", "beautify_llm")
    graph_builder.add_edge("run_compliment_code", "beautify_llm")
    graph_builder.add_edge("beautify_llm", END)

    return graph_builder.compile()


demo2_graph = build_demo2_graph()


if __name__ == "__main__":
    graph = build_demo2_graph()

    payload_question = [
        {
            "time_of_comment": "2025-01-20",
            "customer_remark": "Why has the packaging changed?",
            "social_media_channel": "facebook",
            "number_of_likes": 100,
        }
    ]

    payload_compliment = [
        {
            "time_of_comment": "2025-01-21",
            "customer_remark": "I love your product—great job!",
            "social_media_channel": "instagram",
            "number_of_likes": 42,
        }
    ]

    print("\n=== RUN: QUESTION ===")
    result = graph.invoke({"payload": payload_question})
    print("FINAL RESULT:\n", result)

    print("\nSTREAM:\n")
    for step in graph.stream({"payload": payload_question}):
        print(step)

    print("\n=== RUN: COMPLIMENT ===")
    result = graph.invoke({"payload": payload_compliment})
    print("FINAL RESULT:\n", result)

    print("\nSTREAM:\n")
    for step in graph.stream({"payload": payload_compliment}):
        print(step)
