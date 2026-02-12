from langsmith.evaluation import EvaluationResult, run_evaluator
from langsmith.schemas import Run, Example
import json

@run_evaluator
def json_schema_evaluator(run: Run, example: Example):
    """
    Checks if the output is a valid JSON with the required keys.
    """
    try:
        output = run.outputs
        if not isinstance(output, dict):
            output = json.loads(output)
            
        required_keys = ["label", "reasons", "evidence_links"]
        if all(key in output for key in required_keys):
            return EvaluationResult(key="json_schema_validity", score=1)
        else:
            return EvaluationResult(key="json_schema_validity", score=0, comment="Output is missing required keys.")
            
    except Exception as e:
        return EvaluationResult(key="json_schema_validity", score=0, comment=f"Error parsing JSON: {e}")

@run_evaluator
def evidence_links_evaluator(run: Run, example: Example):
    """
    Checks if evidence_links are present when the label is 'verified'.
    """
    try:
        output = run.outputs
        if not isinstance(output, dict):
            output = json.loads(output)
            
        if output.get("label") == "verified":
            if output.get("evidence_links") and isinstance(output["evidence_links"], list) and len(output["evidence_links"]) > 0:
                return EvaluationResult(key="evidence_links_check", score=1)
            else:
                return EvaluationResult(key="evidence_links_check", score=0, comment="Missing evidence links for 'verified' label.")
        else:
            return EvaluationResult(key="evidence_links_check", score=1) # Not applicable for other labels
            
    except Exception as e:
        return EvaluationResult(key="evidence_links_check", score=0, comment=f"Error during evaluation: {e}")

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


# Placeholder for LLM-as-judge evaluators.
# These would require more complex implementation with prompts and potentially external APIs.

@run_evaluator
def llm_as_judge_factuality_evaluator(run: Run, example: Example):
    """
    A placeholder for an LLM-as-judge factuality evaluator.
    """
    # In a real implementation, you would use an LLM to compare the run's output
    # with the example's expected output and provide a score and rationale.
    return EvaluationResult(key="factuality_llm_judge", score=None, comment="Not implemented")

@run_evaluator
def evidence_quality_evaluator(run: Run, example: Example):
    """
    A placeholder for an evidence quality evaluator.
    """
    return EvaluationResult(key="evidence_quality", score=None, comment="Not implemented")

@run_evaluator
def safety_evaluator(run: Run, example: Example):
    """
    A placeholder for a safety evaluator.
    """
    return EvaluationResult(key="safety", score=None, comment="Not implemented")
