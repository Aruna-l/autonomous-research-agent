"""
schemas.py
-----------
Pydantic models define the STRUCTURE we force the LLM's output into.

Why this matters for an agentic system:
LLMs naturally produce free-flowing text. But if agent.py needs to loop
through "each sub-question" or decide "should I search again: yes/no",
we can't parse that reliably from a paragraph of prose. Pydantic + the
LLM's structured-output / tool-calling mode lets us GUARANTEE the shape
of the data coming back, so the rest of our code can trust it completely.

Every model here maps directly to one step in the agent loop:
  ResearchPlan      -> output of the "planning" step
  SearchResult       -> one result from the Tavily tool
  ReflectionDecision -> output of the "reflect: am I done?" step
  ResearchReport     -> the final synthesized output
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone


class ResearchPlan(BaseModel):
    """
    Output of the PLANNING step.
    The LLM breaks one broad topic into several concrete, searchable
    sub-questions. This is the "task decomposition" concept in action.
    """
    topic: str = Field(..., description="The original research topic given by the user")
    sub_questions: List[str] = Field(
        ...,
        description="3-5 specific, independently searchable sub-questions that together cover the topic",
        min_length=1,
        max_length=6,
    )
    reasoning: str = Field(
        ...,
        description="Brief explanation of why these sub-questions were chosen"
    )


class SearchResult(BaseModel):
    """
    One result returned by the search_web tool (backed by Tavily).
    We normalize Tavily's raw response into this shape so the rest
    of the agent doesn't need to know which search provider we used.
    """
    query: str = Field(..., description="The query that produced this result")
    title: str
    url: str
    content: str = Field(..., description="Snippet or extracted content from the page")
    score: Optional[float] = Field(None, description="Relevance score, if provided by the search API")


class SubQuestionFindings(BaseModel):
    """
    Groups all search results gathered for a single sub-question.
    This is what gets handed to the reflection step and, eventually,
    the report writer.
    """
    sub_question: str
    results: List[SearchResult] = Field(default_factory=list)


class ReflectionDecision(BaseModel):
    """
    Output of the REFLECTION step: the agent looking at what it has
    gathered so far and deciding whether it's enough.

    This is the field that makes the loop "agentic" rather than a fixed
    pipeline -- the LLM itself controls whether another search happens.
    """
    has_enough_information: bool = Field(
        ...,
        description="True if the gathered findings are sufficient to write a confident, well-grounded report"
    )
    missing_information: Optional[str] = Field(
        None,
        description="If not enough info: a short description of what's missing"
    )
    follow_up_query: Optional[str] = Field(
        None,
        description="If not enough info: one specific new search query to fill the gap"
    )


class ResearchReport(BaseModel):
    """
    The final synthesized output of the whole agent run.
    """
    topic: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sub_questions: List[str]
    summary: str = Field(..., description="A short executive-summary paragraph")
    full_report_markdown: str = Field(..., description="The complete report body in markdown, with inline citations")
    sources: List[str] = Field(default_factory=list, description="Deduplicated list of all source URLs used")
    search_rounds: int = Field(1, description="How many rounds of searching the agent performed (tracks reflection loops)")
