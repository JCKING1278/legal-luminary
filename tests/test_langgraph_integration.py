"""Tests for integrated LangGraph agents."""

import pytest


class TestDemo1Graph:
    """Tests for Demo 1 - Heuristic routing."""

    def test_extract_content(self):
        from agent.demo1_graph import extract_content, Demo1State

        state: Demo1State = {
            "text": "",
            "answer": "",
            "payload": [{"customer_remark": "Test question?"}],
        }
        result = extract_content(state)
        assert result["text"] == "Test question?"

    def test_route_question(self):
        from agent.demo1_graph import route_question_or_compliment, Demo1State

        state: Demo1State = {
            "text": "Why did this change?",
            "answer": "",
            "payload": [],
        }
        result = route_question_or_compliment(state)
        assert result == "question"

    def test_route_compliment(self):
        from agent.demo1_graph import route_question_or_compliment, Demo1State

        state: Demo1State = {
            "text": "Great product",
            "answer": "",
            "payload": [],
        }
        result = route_question_or_compliment(state)
        assert result == "compliment"

    def test_build_graph(self):
        from agent.demo1_graph import build_demo1_graph

        graph = build_demo1_graph()
        assert graph is not None


class TestQuiz1Graph:
    """Tests for Quiz 1 - Vague Specification Detection."""

    def test_check_vagueness_vague(self):
        from agent.quiz1_graph import check_vagueness, Quiz1State

        state: Quiz1State = {
            "specification": "The system shall be fast",
            "is_vague": False,
            "clarified_spec": "",
            "test_case": "",
        }
        result = check_vagueness(state)
        assert result["is_vague"] is True

    def test_check_vagueness_not_vague(self):
        from agent.quiz1_graph import check_vagueness, Quiz1State

        state: Quiz1State = {
            "specification": "Response time shall be less than 200ms",
            "is_vague": False,
            "clarified_spec": "",
            "test_case": "",
        }
        result = check_vagueness(state)
        assert result["is_vague"] is False

    def test_fix_vagueness(self):
        from agent.quiz1_graph import fix_vagueness, Quiz1State

        state: Quiz1State = {
            "specification": "The system shall be fast and easy to use",
            "is_vague": True,
            "clarified_spec": "",
            "test_case": "",
        }
        result = fix_vagueness(state)
        assert "response time < 200ms" in result["clarified_spec"]

    def test_route_after_check(self):
        from agent.quiz1_graph import route_after_check, Quiz1State

        state_vague: Quiz1State = {
            "specification": "test",
            "is_vague": True,
            "clarified_spec": "",
            "test_case": "",
        }
        assert route_after_check(state_vague) == "fix"

        state_not_vague: Quiz1State = {
            "specification": "test",
            "is_vague": False,
            "clarified_spec": "",
            "test_case": "",
        }
        assert route_after_check(state_not_vague) == "testcase"

    def test_build_graph(self):
        from agent.quiz1_graph import build_quiz1_graph

        graph = build_quiz1_graph()
        assert graph is not None


class TestIntegratedGraph:
    """Tests for the main integrated graph."""

    def test_graph_imports(self):
        from agent.graph import graph, GraphType, State, Context

        assert graph is not None
        assert GraphType is not None
        assert State is not None
        assert Context is not None

    def test_route_to_graph(self):
        from agent.graph import route_to_graph, State

        state: State = {
            "graph_type": "demo1",
            "payload": [],
            "specification": "",
            "content_type": "",
            "query": "",
            "raw_content": "",
            "result": {},
        }
        result = route_to_graph(state)
        assert result == "demo1"

    def test_graph_compiles(self):
        from agent.graph import graph

        assert graph.name == "Legal Luminary Integrated LangGraph"
