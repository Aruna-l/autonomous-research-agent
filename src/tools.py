"""
tools.py
--------
This file defines the agent's ONE tool: web search.

Two things live here, and it's important to understand why both exist:

1. `search_web()` - the actual Python function that does the work
   (calls Tavily's API, returns clean SearchResult objects).

2. `SEARCH_TOOL_SCHEMA` - a JSON description of that function that we
   hand to the LLM. This is the "function calling" contract: the LLM
   never runs code itself. It reads this schema, decides "I want to
   call search_web with query=X", and outputs that decision as
   structured data. OUR code then calls the real Python function and
   feeds the result back to the LLM. The LLM is the decision-maker;
   our code is the hands.
"""

import os
from typing import List
from tavily import TavilyClient
from src.schemas import SearchResult

_tavily_client = None


def _get_client() -> TavilyClient:
    """Lazy-init so importing this module doesn't require the API key to be set yet."""
    global _tavily_client
    if _tavily_client is None:
        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            raise RuntimeError(
                "TAVILY_API_KEY not found in environment. "
                "Add it to your .env file (see .env.example)."
            )
        _tavily_client = TavilyClient(api_key=api_key)
    return _tavily_client


def search_web(query: str, max_results: int = 4) -> List[SearchResult]:
    """
    Runs a web search via Tavily and returns normalized SearchResult objects.

    This is the function the "agent" calls whenever it decides (via the LLM)
    that it needs external information. Tavily is used instead of raw
    Google/Bing because it returns pre-cleaned, LLM-ready content instead
    of raw HTML you'd have to parse yourself.
    """
    client = _get_client()

    try:
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",  # "advanced" digs deeper than "basic", better for research
        )
    except Exception as e:
        # Agents in production must handle tool failures gracefully --
        # a failed search shouldn't crash the whole run.
        print(f"[tools.search_web] Search failed for query '{query}': {e}")
        return []

    results = []
    for item in response.get("results", []):
        results.append(
            SearchResult(
                query=query,
                title=item.get("title", "Untitled"),
                url=item.get("url", ""),
                content=item.get("content", ""),
                score=item.get("score"),
            )
        )
    return results


# ---------------------------------------------------------------------------
# Tool schema in Gemini's function-declaration format.
# Not currently invoked by agent.py (search is called deterministically per
# sub-question there), but kept here to demonstrate the function-calling
# contract: this is what you'd hand to Gemini's `tools=[...]` config if you
# wanted the MODEL itself to decide when and how to search, rather than your
# code deciding for it. Good to mention in an interview as "the next step"
# for making the agent's tool use fully autonomous rather than scripted.
# ---------------------------------------------------------------------------
SEARCH_TOOL_SCHEMA = {
    "name": "search_web",
    "description": (
        "Search the web for current, factual information on a specific query. "
        "Use this whenever you need up-to-date information you don't already have, "
        "or need to verify a claim before including it in a report."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A specific, well-formed search query. Avoid vague or overly broad queries.",
            }
        },
        "required": ["query"],
    },
}