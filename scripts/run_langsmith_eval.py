import os
from langsmith import Client, evaluate
from verifier.website_checker import verify_website
from verifier.news_checker import verify_news_article
from evals.custom_evaluators import (
    json_schema_evaluator,
    evidence_links_evaluator,
    llm_as_judge_factuality_evaluator,
    evidence_quality_evaluator,
    safety_evaluator,
    qa_evaluator,
)

# This should be configured with your API keys
# os.environ["LANGCHAIN_API_KEY"] = "..."
# os.environ["OPENAI_API_KEY"] = "..."

def run_evaluation():
    """
    Runs the LangSmith evaluation and checks the results.
    """
    client = Client()
    
    # These should match the names of your datasets in LangSmith
    website_dataset_name = "website-content-checks"
    news_dataset_name = "news-validation"
    
    # These should match the names of your chains in LangSmith
    website_checker_project_name = "website-checker-eval"
    news_checker_project_name = "news-checker-eval"
    
    # Define the evaluators to use
    evaluators = [
        json_schema_evaluator,
        evidence_links_evaluator,
        llm_as_judge_factuality_evaluator,
        evidence_quality_evaluator,
        safety_evaluator,
        qa_evaluator,
    ]
    
    # Fetch datasets
    website_dataset = client.list_examples(dataset_name=website_dataset_name)
    news_dataset = client.list_examples(dataset_name=news_dataset_name)

    # Run evaluation for the website checker
    evaluate(
        verify_website,
        data=website_dataset,
        evaluators=evaluators,
        experiment_prefix=website_checker_project_name,
    )
    
    # Run evaluation for the news checker
    evaluate(
        verify_news_article,
        data=news_dataset,
        evaluators=evaluators,
        experiment_prefix=news_checker_project_name,
    )
    
    print("All evaluations complete.")

if __name__ == "__main__":
    run_evaluation()
