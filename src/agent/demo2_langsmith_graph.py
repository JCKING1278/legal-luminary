"""LangGraph Demo 2 with LangSmith: LLM-based routing with tracing.

This demo shows a LangGraph that uses an LLM (Ollama) to classify
customer feedback as either a question or compliment, with LangSmith
tracing enabled for observability.

Integrated from CS5474 Software V&V course - LangGraph Hands-on 2.
"""

from __future__ import annotations

import json
import os
from typing_extensions import TypedDict, Literal

from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama


def get_langsmith_callbacks():
    """Get LangSmith callbacks if tracing is enabled."""
    tracing = os.getenv("LANGCHAIN_TRACING_V2", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
    }
    if not tracing:
        return []

    api_key = os.getenv("LANGCHAIN_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "LangSmith tracing is enabled (LANGCHAIN_TRACING_V2=true) but "
            "LANGCHAIN_API_KEY is missing. Set LANGCHAIN_API_KEY to your "
            "LangSmith API key (and optionally LANGCHAIN_PROJECT). "
        )

    from langchain.callbacks.tracers import LangChainTracer

    project = (
        os.getenv("LANGCHAIN_PROJECT", "LangGraph_Demo2").strip() or "LangGraph_Demo2"
    )
    tracer = LangChainTracer(project_name=project)
    return [tracer]


Route = Literal["question", "compliment"]


class Demo2LangSmithState(TypedDict):
    """State for Demo 2 with LangSmith graph."""

    payload: list[dict]
    text: str
    route: Route
    answer: str


def extract_content(state: Demo2LangSmithState) -> dict:
    """Extract text from payload."""
    return {"text": state["payload"][0]["customer_remark"]}


def llm_route(state: Demo2LangSmithState) -> dict:
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
        route = str(obj.get("route", "")).strip().lower()
    except Exception:
        route = raw.lower()

    if "question" in route:
        return {"route": "question"}
    if "compliment" in route:
        return {"route": "compliment"}

    return {"route": "question"}


def route_from_state(state: Demo2LangSmithState) -> Route:
    """Return the route from state."""
    return state["route"]


def run_compliment_code(state: Demo2LangSmithState) -> dict:
    """Handle compliment."""
    return {"answer": "Thanks for the compliment."}


def run_question_code(state: Demo2LangSmithState) -> dict:
    """Handle question."""
    return {"answer": "Thanks for your question. We will look into it."}


def beautify_llm(state: Demo2LangSmithState) -> dict:
    """Beautify response using LLM."""
    llm = ChatOllama(model="granite-code:20b", temperature=0)

    prompt = (
        "Rewrite the following customer-service reply politely in ONE short sentence.\n"
        "Do not add new facts.\n\n"
        f"Reply: {state['answer']}"
    )

    pretty = llm.invoke(prompt).content.strip()
    return {"answer": pretty}


def build_demo2_langsmith_graph() -> StateGraph:
    """Build and return the Demo 2 LangSmith graph."""
    graph_builder = StateGraph(Demo2LangSmithState)

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


demo2_langsmith_graph = build_demo2_langsmith_graph()


if __name__ == "__main__":
    graph = build_demo2_langsmith_graph()

    try:
        png_bytes = graph.get_graph().draw_mermaid_png()
        with open("langgraph_demo2_diagram.png", "wb") as f:
            f.write(png_bytes)
        print("Diagram saved as: langgraph_demo2_diagram.png")
    except Exception as e:
        print("(Optional) Could not generate diagram PNG:", e)

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

    callbacks = get_langsmith_callbacks()
    config = {"callbacks": callbacks} if callbacks else None

    print("\n=== RUN: QUESTION ===")
    result = graph.invoke({"payload": payload_question}, config=config)
    print("FINAL RESULT:\n", result)

    print("\nSTREAM:\n")
    for step in graph.stream({"payload": payload_question}, config=config):
        print(step)

    print("\n=== RUN: COMPLIMENT ===")
    result = graph.invoke({"payload": payload_compliment}, config=config)
    print("FINAL RESULT:\n", result)

    print("\nSTREAM:\n")
    for step in graph.stream({"payload": payload_compliment}, config=config):
        print(step)
