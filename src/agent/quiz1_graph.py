"""Quiz 1: LangGraph Vague Specification Detection Agent.

This agent takes a short specification as input and:
1. Determines whether the specification is vague or not vague
2. If not vague: Creates a test case specification
3. If vague: Transforms it to a precise specification, then creates a test case

Designed for CS5374 Software Verification and Validation.
Integrated from course project materials.
"""

from __future__ import annotations

import os
from typing_extensions import TypedDict

from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


def get_llm():
    """Get the LLM instance based on available API keys."""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key:
        return ChatOpenAI(model="gpt-4", api_key=openai_key, temperature=0)
    return None


class Quiz1State(TypedDict):
    """State for Quiz 1 graph."""

    specification: str
    is_vague: bool
    clarified_spec: str
    test_case: str


def check_vagueness(state: Quiz1State) -> dict:
    """Determine if the specification is vague or not."""
    spec = state["specification"]
    llm = get_llm()

    if llm:
        messages = [
            SystemMessage(
                content="""You are a specification analyzer.
Determine if the following requirement is vague or unclear.
Consider: missing metrics, undefined terms, ambiguous language.
Respond with only 'VAGUE' or 'NOT_VAGUE'."""
            ),
            HumanMessage(content=spec),
        ]
        response = llm.invoke(messages)
        is_vague = "VAGUE" in response.content.upper()
    else:
        vague_indicators = [
            "fast",
            "easy",
            "high-quality",
            "timely",
            "as appropriate",
            "secure",
            "user-friendly",
            "efficient",
            "robust",
            "scalable",
        ]
        is_vague = any(indicator in spec.lower() for indicator in vague_indicators)

    return {"is_vague": is_vague}


def fix_vagueness(state: Quiz1State) -> dict:
    """Transform a vague specification into a precise one."""
    spec = state["specification"]
    llm = get_llm()

    if llm:
        messages = [
            SystemMessage(
                content="""You are a requirements engineer.
Transform the following vague specification into a precise,
testable requirement. Be specific and include measurable criteria.
Return ONLY the clarified specification, no explanation."""
            ),
            HumanMessage(content=spec),
        ]
        response = llm.invoke(messages)
        clarified = response.content.strip()
    else:
        clarifications = {
            "fast": "response time < 200ms",
            "easy": "requires <= 3 clicks",
            "high-quality": "meets ISO 9001 standards",
            "timely": "within 2 business days",
            "as appropriate": "per investigation protocol Section 4.2",
            "secure": "TLS 1.3 with AES-256 encryption",
            "user-friendly": "usability score >= 4.5/5",
            "efficient": "resource utilization < 80%",
            "robust": "99.9% uptime with automatic failover",
            "scalable": "supports 10x current load",
        }

        clarified = spec
        for vague_term, clarification in clarifications.items():
            if vague_term in clarified.lower():
                clarified = clarified.replace(vague_term, f"[{clarification}]")

    return {"clarified_spec": clarified}


def generate_test_case(state: Quiz1State) -> dict:
    """Generate a test case specification."""
    spec = state.get("clarified_spec", state["specification"])
    is_vague = state["is_vague"]
    llm = get_llm()

    if llm:
        messages = [
            SystemMessage(
                content="""You are a test engineer.
Create a detailed test case specification including:
- Input: specific test inputs
- Expected Output: expected behavior
- Preconditions: required conditions
Format as structured text. Be specific and measurable."""
            ),
            HumanMessage(content=spec),
        ]
        response = llm.invoke(messages)
        test_case = response.content.strip()
    else:
        test_case = f"""Test Case Specification:
- Input: {spec}
- Expected Output: System should meet all specified criteria
- Preconditions: System must be operational, test data available
- Vague Original: {is_vague}"""

    return {"test_case": test_case}


def route_after_check(state: Quiz1State) -> str:
    """Decide next step based on whether spec is vague."""
    if state["is_vague"]:
        return "fix"
    return "testcase"


def build_quiz1_graph():
    """Build the Quiz 1 LangGraph agent."""
    graph = StateGraph(Quiz1State)

    graph.add_node("check", check_vagueness)
    graph.add_node("fix", fix_vagueness)
    graph.add_node("testcase", generate_test_case)

    graph.set_entry_point("check")

    graph.add_conditional_edges(
        "check", route_after_check, {"fix": "fix", "testcase": "testcase"}
    )

    graph.add_edge("fix", "testcase")
    graph.add_edge("testcase", END)

    return graph.compile()


quiz1_graph = build_quiz1_graph()


VAGUE_SPECIFICATIONS = [
    "The system shall allow for fast, easy data entry",
    "Install high-quality flooring",
    "The application must be secure",
    "The report will include, as appropriate, investigation findings",
    "The project will be completed in a timely manner",
]


if __name__ == "__main__":
    agent = build_quiz1_graph()

    print("=" * 60)
    print("Quiz 1: LangGraph Vague Specification Detection Agent")
    print("=" * 60)

    for spec in VAGUE_SPECIFICATIONS:
        print(f"\nInput: {spec}")
        print("-" * 40)

        result = agent.invoke({"specification": spec})

        print(f"Is Vague: {result['is_vague']}")
        if result.get("clarified_spec"):
            print(f"Clarified: {result['clarified_spec']}")
        print(f"Test Case:\n{result['test_case']}")
        print("=" * 60)
