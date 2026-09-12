"""
agent.py
--------
THE CORE OF THE PROJECT.

This is the agent loop: plan -> search -> reflect -> (search again if needed) -> synthesize.
Everything else in this repo (API, frontend, automation) is just a way of
TRIGGERING this function. If you only deeply understand one file for your
interview, make it this one.

Flow:
  1. PLAN     - ask Claude to break the topic into sub-questions
  2. SEARCH   - for each sub-question, call the search_web tool
  3. REFLECT  - ask Claude: "is this enough, or is something missing?"
  4. (loop back to SEARCH with a follow-up query if reflection says so,
      capped at MAX_REFLECTION_ROUNDS so it can't run forever)
  5. SYNTHESIZE - write the final grounded markdown report

Each step is a generator-friendly function (yields progress strings) so
the Streamlit frontend can show live progress instead of a blank spinner.
"""

from typing import List, Generator, Tuple
from src.schemas import (
    ResearchPlan,
    SubQuestionFindings,
    ReflectionDecision,
    ResearchReport,
)
from src.llm_client import plan_research, reflect, synthesize_report
from src.tools import search_web

MAX_REFLECTION_ROUNDS = 2  # guardrail: prevents infinite search loops


def run_research_agent(topic: str) -> Generator[str, None, ResearchReport]:
    """
    Runs the full agent loop for a given topic.

    This is a generator: it `yield`s human-readable progress strings as it
    works (useful for streaming into a UI), and returns the final
    ResearchReport via StopIteration.value when exhausted.

    If you just want the final result without progress streaming, use
    `run_research_agent_sync()` below instead.
    """
    # --- STEP 1: PLAN ---
    yield f"Planning sub-questions for: '{topic}'..."
    plan: ResearchPlan = plan_research(topic)
    yield f"Plan ready. {len(plan.sub_questions)} sub-questions identified:"
    for i, sq in enumerate(plan.sub_questions, 1):
        yield f"   {i}. {sq}"

    # --- STEP 2: INITIAL SEARCH (one search per sub-question) ---
    findings: List[SubQuestionFindings] = []
    for sq in plan.sub_questions:
        yield f"Searching: {sq}"
        results = search_web(sq)
        findings.append(SubQuestionFindings(sub_question=sq, results=results))
        yield f"   -> found {len(results)} results"

    # --- STEP 3 & 4: REFLECT, loop if needed ---
    search_rounds = 1
    for round_num in range(MAX_REFLECTION_ROUNDS):
        yield "Reflecting: checking if findings are sufficient..."
        decision: ReflectionDecision = reflect(topic, findings)

        if decision.has_enough_information:
            yield "Enough information gathered. Proceeding to write report."
            break

        if not decision.follow_up_query:
            # Model flagged a gap but gave no actionable query -- stop looping.
            yield "Gap identified but no actionable follow-up query given. Proceeding anyway."
            break

        yield f"Gap found: {decision.missing_information}"
        yield f"Follow-up search: {decision.follow_up_query}"
        follow_up_results = search_web(decision.follow_up_query)
        findings.append(
            SubQuestionFindings(
                sub_question=decision.follow_up_query,
                results=follow_up_results,
            )
        )
        search_rounds += 1
        yield f"   -> found {len(follow_up_results)} additional results"
    else:
        yield f"Reached max reflection rounds ({MAX_REFLECTION_ROUNDS}). Proceeding with what we have."

    # --- STEP 5: SYNTHESIZE ---
    yield "Writing final report..."
    report_markdown = synthesize_report(topic, plan.sub_questions, findings)

    all_sources = list({r.url for f in findings for r in f.results if r.url})

    report = ResearchReport(
        topic=topic,
        sub_questions=plan.sub_questions,
        summary=report_markdown.split("\n\n")[0][:500],  # first paragraph as a quick summary
        full_report_markdown=report_markdown,
        sources=all_sources,
        search_rounds=search_rounds,
    )
    yield "Done."
    return report


def run_research_agent_sync(topic: str) -> ResearchReport:
    """
    Convenience wrapper for callers that don't need live progress
    (e.g. the automation script). Drains the generator and returns
    just the final ResearchReport.
    """
    gen = run_research_agent(topic)
    report = None
    try:
        while True:
            next(gen)
    except StopIteration as stop:
        report = stop.value
    return report
