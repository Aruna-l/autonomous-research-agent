"""
llm_client.py
-------------
All calls to the Gemini API live here.

Unlike Claude (which needs a "forced tool call" trick to get reliable JSON
back), Gemini has NATIVE structured output: you pass a Pydantic model as
`response_schema` with `response_mime_type="application/json"`, and the
SDK returns an already-parsed instance of that model via `response.parsed`.
This is simpler and more direct -- worth mentioning in an interview as a
concrete difference between provider APIs you evaluated hands-on.

Two call patterns are used here:

1. STRUCTURED OUTPUT (plan_research, reflect) -- we pass our Pydantic
   schema directly as response_schema. Gemini guarantees the response
   matches that shape.

2. FREE TEXT (synthesize_report) -- for the final report we want natural
   markdown prose, so no schema is passed, just a plain generation call.
"""

import os
from typing import List
from google import genai
from google.genai import types

from src.schemas import ResearchPlan, ReflectionDecision, SubQuestionFindings

_client = None
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not found in environment. "
                "Add it to your .env file (see .env.example)."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def plan_research(topic: str) -> ResearchPlan:
    """
    STEP 1 of the agent loop: PLANNING.
    Takes a broad topic and breaks it into concrete, independently
    searchable sub-questions. Gemini returns this already validated
    against the ResearchPlan schema.
    """
    client = _get_client()

    system_instruction = (
        "You are a research planning assistant. Given a topic, break it into "
        "3-5 specific, independently searchable sub-questions that together "
        "give a comprehensive picture of the topic. Avoid overlap between "
        "sub-questions. Each should be answerable via a focused web search."
    )

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=f"Topic: {topic}",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=ResearchPlan,
        ),
    )

    plan: ResearchPlan = response.parsed
    if plan is None:
        raise RuntimeError(f"Gemini did not return a valid ResearchPlan. Raw text: {response.text}")
    return plan


def reflect(topic: str, findings: List[SubQuestionFindings]) -> ReflectionDecision:
    """
    STEP 3 of the agent loop: REFLECTION.
    Looks at everything gathered so far and decides whether it's enough,
    or whether one more targeted search is needed. This is the step that
    makes the pipeline "agentic" -- the model controls the loop, not fixed code.
    """
    client = _get_client()

    system_instruction = (
        "You are a research quality reviewer. Given a topic and the search "
        "findings gathered so far, decide if there is enough grounded "
        "information to write a confident, well-sourced report. If not, "
        "identify the single most important gap and propose one specific "
        "follow-up search query to fill it."
    )

    findings_text = _format_findings_for_prompt(findings)
    user_message = f"Topic: {topic}\n\nFindings so far:\n{findings_text}"

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=ReflectionDecision,
        ),
    )

    decision: ReflectionDecision = response.parsed
    if decision is None:
        raise RuntimeError(f"Gemini did not return a valid ReflectionDecision. Raw text: {response.text}")
    return decision


def synthesize_report(topic: str, sub_questions: List[str], findings: List[SubQuestionFindings]) -> str:
    """
    STEP 4 of the agent loop: SYNTHESIS.
    Writes the final markdown report as free text (no schema) because we
    want natural, well-formatted prose here rather than constrained JSON.

    Grounding note: the prompt explicitly instructs the model to only use
    the provided findings, not its own memory -- this is what prevents
    hallucinated facts from ending up in the report.
    """
    client = _get_client()
    findings_text = _format_findings_for_prompt(findings)

    system_instruction = (
        "You are a research report writer. Write a clear, well-structured "
        "markdown report based ONLY on the provided search findings below. "
        "Do not use outside knowledge or invent facts not present in the "
        "findings. Cite sources inline using [Source: URL] after claims. "
        "Structure: a short executive summary, then a section per sub-question, "
        "then a 'Sources' list at the end."
    )

    user_message = (
        f"Topic: {topic}\n\n"
        f"Sub-questions covered: {', '.join(sub_questions)}\n\n"
        f"Findings:\n{findings_text}"
    )

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
        ),
    )

    return response.text


def _format_findings_for_prompt(findings: List[SubQuestionFindings]) -> str:
    """Flattens SubQuestionFindings into a readable text block for prompts."""
    lines = []
    for finding in findings:
        lines.append(f"\n### Sub-question: {finding.sub_question}")
        if not finding.results:
            lines.append("(No search results found for this sub-question)")
        for r in finding.results:
            lines.append(f"- [{r.title}]({r.url}): {r.content[:400]}")
    return "\n".join(lines)