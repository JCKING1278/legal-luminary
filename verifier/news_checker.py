import os
from typing import TypedDict, Annotated, List
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END, START

# This should be configured with your API keys
# os.environ["OPENAI_API_KEY"] = "..."

# Truncate content to this many characters to avoid exceeding model context window
MAX_CONTENT_LENGTH = 12000 # Roughly 3000 tokens

class VerifyNewsState(TypedDict):
    url: str
    content: str
    verification_result: dict

def fetch_content(state: VerifyNewsState):
    """Fetches the content of a news article."""
    loader = WebBaseLoader(state["url"])
    docs = loader.load()
    content = " ".join([doc.page_content for doc in docs])
    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH]
    return {"content": content, **state}

def run_verification(state: VerifyNewsState):
    """Runs the verification chain using LCEL."""
    llm = OpenAI(temperature=0)
    template = """
    You are a news content verifier. Your task is to analyze the content of the given news article URL and determine if it is "verified", "uncertain", or "misleading".
    
    URL: {url}
    
    Content:
    {content}
    
    Based on the content, provide a verification label, a brief reason for your decision, and a list of evidence links that support your conclusion.
    
    Provide your output in the following JSON format:
    {{
        "label": "verified|uncertain|misleading",
        "reasons": "...",
        "evidence_links": ["...", "..."]
    }}
    
    Output:
    """
    prompt = PromptTemplate(template=template, input_variables=["url", "content"])
    parser = JsonOutputParser()

    chain = prompt | llm | parser

    result = chain.invoke({"url": state["url"], "content": state["content"]})
    return {"verification_result": result, **state}

def get_news_verifier_graph():
    """Returns a compiled LangGraph for verifying news articles."""
    graph_builder = StateGraph(VerifyNewsState)
    
    graph_builder.add_node("fetch_content", fetch_content)
    graph_builder.add_node("run_verification", run_verification)
    
    graph_builder.add_edge(START, "fetch_content")
    graph_builder.add_edge("fetch_content", "run_verification")
    graph_builder.add_edge("run_verification", END)
    
    app = graph_builder.compile()
    return app

def verify_news_article(input: dict) -> dict:
    """Verifies the content of a news article using the LangGraph."""
    url = input["url"]
    app = get_news_verifier_graph()
    initial_state = {"url": url}
    final_state = app.invoke(initial_state)
    return final_state["verification_result"]

if __name__ == "__main__":
    # Example from the news feed
    test_url = "https://kdhnews.com/news/local/crime/harker-heights-man-accused-of-shooting-into-home-with-people-inside/article_1de5f1d6-c9fd-11ee-8f0a-93bdc60b86a3.html"
    verification = verify_news_article({"url": test_url})
    print(verification)
