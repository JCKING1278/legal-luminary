# LangGraph Integration Report

## Overview

This document describes the integration of LangGraph hands-on modules from CS5474 Software V&V into the Legal Luminary project.

## Integrated Components

### 1. LangGraph Hands-On 1 (06_langgraph_hands_on_1)

**Source:** `/run/media/sdw3098/14GPARTFOUR/CS5474_SOFTWARE_VV/06_langgraph_hands_on_1`

**Integrated as:** `src/agent/demo1_graph.py`

**Description:** Simple heuristic routing for customer feedback processing. Routes feedback to question or compliment handlers based on presence of '?' character.

**Key Features:**
- State-based workflow with TypedDict
- Conditional routing based on content analysis
- Simple beautification of responses

### 2. LangGraph Hands-On 2 (08_langgraph_hands_on_2)

**Source:** `/run/media/sdw3098/14GPARTFOUR/CS5474_SOFTWARE_VV/08_langgraph_hands_on_2`

**Integrated as:** 
- `src/agent/demo2_graph.py` - LLM-based routing with Ollama
- `src/agent/demo2_langsmith_graph.py` - LLM routing with LangSmith tracing

**Description:** LLM-based routing for customer feedback using Ollama (granite-code:20b) for classification and beautification.

**Key Features:**
- LLM-based content classification
- JSON response parsing with fallback
- LangSmith tracing support for observability

### 3. Quiz 1 - Vague Specification Detection

**Source:** `/run/media/sdw3098/14GPARTFOUR/CS5474_SOFTWARE_VV/project/src/agent/`

**Integrated as:**
- `src/agent/quiz1_graph.py` - Vague specification detection
- `src/agent/quiz1_langsmith_graph.py` - Vague spec detection with LangSmith tracing

**Description:** Agent that detects vague specifications, transforms them into precise requirements, and generates test cases.

**Key Features:**
- Specification vagueness detection
- Automatic clarification of vague terms
- Test case generation
- Heuristic fallback when LLM unavailable

### 4. Main Integrated Graph

**File:** `src/agent/graph.py`

**Description:** Unified routing graph that dispatches to appropriate sub-graphs based on `graph_type` parameter.

**Supported Graph Types:**
- `demo1` - Heuristic routing
- `demo2` - LLM routing with Ollama
- `demo2_langsmith` - LLM routing with LangSmith tracing
- `quiz1` - Vague specification detection
- `quiz1_langsmith` - Vague spec detection with LangSmith
- `validation_pipeline` - Legal content validation

## Configuration Files

### pyproject.toml
Updated with LangGraph dependencies:
- langgraph>=1.0.0
- langchain>=0.3.0
- langchain-openai>=0.2.0
- langchain-ollama>=0.2.0
- python-dotenv>=1.0.1
- typing_extensions>=4.0.0

### langgraph.json
Configuration for LangGraph Server deployment.

### .env.example
Template for environment variables including:
- OpenAI API key
- LangSmith tracing configuration
- Ollama configuration

## Architecture

```
legal-luminary/
├── src/
│   └── agent/
│       ├── __init__.py
│       ├── graph.py              # Main integrated graph
│       ├── demo1_graph.py        # Heuristic routing
│       ├── demo2_graph.py        # LLM routing (Ollama)
│       ├── demo2_langsmith_graph.py  # LLM routing (LangSmith)
│       ├── quiz1_graph.py        # Vague spec detection
│       └── quiz1_langsmith_graph.py  # Vague spec (LangSmith)
├── validators/                   # Existing validation modules
├── config/                       # Configuration settings
├── orchestrator.py              # Main orchestrator
├── pipeline.py                  # Validation pipeline
├── state.py                     # Core state schema
├── langgraph.json               # LangGraph server config
└── pyproject.toml               # Python project config
```

## Usage

### Running Individual Demos

```python
from agent.demo1_graph import build_demo1_graph

graph = build_demo1_graph()
result = graph.invoke({"payload": [{"customer_remark": "Why did this change?"}]})
```

### Running Integrated Graph

```python
from agent.graph import graph

# Run Quiz 1 agent
result = graph.invoke({
    "graph_type": "quiz1",
    "specification": "The system shall be fast"
})

# Run validation pipeline
result = graph.invoke({
    "graph_type": "validation_pipeline",
    "content_type": "judge",
    "query": "Chief Justice John Roberts"
})
```

### Using LangGraph Server

```bash
# Install LangGraph CLI
pip install langgraph-cli[inmem]

# Start the server
langgraph dev
```

## Project Plan Alignment

This integration supports the **Trustworthy AI Legal and Governmental Content Validator** project plan by:

1. **LangGraph Validator Nodes** - Implements explicit pass/fail routing as described in Hypothesis 2
2. **LangSmith Integration** - Enables tracing and evaluation as specified in the tool integration plan
3. **Modular Architecture** - Supports the validator suite expansion for different content types
4. **Texas Data Integration** - Existing validators use Texas Open Data as authoritative sources

## Next Steps

1. Add experiments module for baseline hallucination rate testing
2. Implement DeepEval/Ragas evaluation metrics
3. Add GARAK security testing integration
4. Expand validators for additional content types
5. Add human-in-the-loop escalation workflow

## References

- PROJECT_PLAN.md - Full project specification
- Collection_of_frameworks_tools_projects.md - Tool references
- LangGraph Documentation - https://langchain-ai.github.io/langgraph
- LangSmith Documentation - https://docs.langchain.com/langsmith
