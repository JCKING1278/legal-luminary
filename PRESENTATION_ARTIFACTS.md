
# LangSmith Presentation Artifacts

This document summarizes the artifacts generated in LangSmith for your presentation on the content validation and generation pipeline. These artifacts demonstrate the key components of the system, including the LangGraph-based verifiers, the custom evaluators, and the overall evaluation process.

## LangSmith Experiments

The evaluation script has generated two experiments in your LangSmith project, one for each verifier:

*   **Website Checker Evaluation:**
    *   **Experiment:** `website-checker-eval-eab2400f`
    *   **Link:** [https://smith.langchain.com/o/5136fb89-e25e-5e2a-a87c-b9335c8c3a15/datasets/82293850-cc7d-44e1-8bc7-79766dcbe007/compare?selectedSessions=90d536dc-67cf-44b3-a00c-d7df14180c2f](https://smith.langchain.com/o/5136fb89-e25e-5e2a-a87c-b9335c8c3a15/datasets/82293850-cc7d-44e1-8bc7-79766dcbe007/compare?selectedSessions=90d536dc-67cf-44b3-a00c-d7df14180c2f)

*   **News Checker Evaluation:**
    *   **Experiment:** `news-checker-eval-90fe8b50`
    *   **Link:** [https://smith.langchain.com/o/5136fb89-e25e-5e2a-a87c-b9335c8c3a15/datasets/e007d4ef-9c92-4817-a58f-19d7c65a5763/compare?selectedSessions=602af79e-5cfe-4b1a-b7f4-e2fd41304d9b](https://smith.langchain.com/o/5136fb89-e25e-5e2a-a87c-b9335c8c3a15/datasets/e007d4ef-9c92-4817-a58f-19d7c65a5763/compare?selectedSessions=602af79e-5cfe-4b1a-b7f4-e2fd41304d9b)

You can use these links to navigate directly to the comparison view in LangSmith, which provides a great overview of the evaluation results.

## Key Traces to Showcase

Within the experiments, you can select individual runs to see the detailed traces. Here are a few examples you can use to showcase the pipeline's functionality:

*   **A successful verification of a news article:**
    *   Navigate to the "news-checker-eval" experiment.
    *   Click on any of the runs in the table.
    *   In the trace view, you can see the execution of the LangGraph, from fetching the content to the final JSON output.
    *   This demonstrates the deterministic nature of the generation process.

*   **A successful verification of a website:**
    *   Navigate to the "website-checker-eval" experiment.
    *   Select a run to showcase the verification of a website, such as the official City of Killeen website.

## Evaluator Showcase

In the "Feedback" section of each run's trace, you can see the results from the different evaluators. This is a great way to demonstrate how you are enforcing quality gates.

You can highlight:
*   **`json_schema_validity`:** This rule-based evaluator checks if the output is a valid JSON with the required keys.
*   **`evidence_links_check`:** This evaluator ensures that evidence links are provided when the content is labeled as "verified".
*   **`qa_correctness`:** This simple QA evaluator compares the predicted label with the ground truth label from the dataset.

## Code Snippets for Your Presentation

Here are some code snippets you can use to explain the implementation of the pipeline.

### LangGraph Verifier (`verifier/website_checker.py`)

This snippet shows the definition of the LangGraph for the website verifier. It highlights the state, the nodes, and the graph structure.

```python
import os
from typing import TypedDict, Annotated, List
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END, START

# ... (rest of the file)

class VerifyWebsiteState(TypedDict):
    url: str
    content: str
    verification_result: dict

def fetch_content(state: VerifyWebsiteState):
    # ...

def run_verification(state: VerifyWebsiteState):
    # ...

def get_website_verifier_graph():
    """Returns a compiled LangGraph for verifying websites."""
    graph_builder = StateGraph(VerifyWebsiteState)
    
    graph_builder.add_node("fetch_content", fetch_content)
    graph_builder.add_node("run_verification", run_verification)
    
    graph_builder.add_edge(START, "fetch_content")
    graph_builder.add_edge("fetch_content", "run_verification")
    graph_builder.add_edge("run_verification", END)
    
    app = graph_builder.compile()
    return app

def verify_website(input: dict) -> dict:
    """Verifies the content of a website using the LangGraph."""
    url = input["url"]
    app = get_website_verifier_graph()
    initial_state = {"url": url}
    final_state = app.invoke(initial_state)
    return final_state["verification_result"]
```

### Custom Evaluators (`evals/custom_evaluators.py`)

This snippet shows the implementation of the custom rule-based evaluators.

```python
from langsmith.evaluation import EvaluationResult, run_evaluator
from langsmith.schemas import Run, Example
import json

@run_evaluator
def json_schema_evaluator(run: Run, example: Example):
    # ...

@run_evaluator
def evidence_links_evaluator(run: Run, example: Example):
    # ...

@run_evaluator
def qa_evaluator(run: Run, example: Example):
    """
    A simple QA evaluator that checks if the predicted label matches the reference label.
    """
    if run.outputs and example.outputs:
        predicted_label = run.outputs.get("label")
        reference_label = example.outputs.get("label")

        is_correct = predicted_label == reference_label
        return {"score": is_correct, "key": "qa_correctness"}
    return {"score": False, "key": "qa_correctness", "comment": "Missing outputs"}
```

By using these artifacts, you can create a compelling presentation that showcases a robust and well-designed content validation and generation pipeline using LangSmith and LangGraph.
