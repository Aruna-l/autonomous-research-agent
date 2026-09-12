"""
tests/test_agent.py
--------------------
Deliberately lightweight tests that don't require real API keys or network
access (so they run in CI). They check:
1. Schemas validate/reject data correctly.
2. report_writer produces a well-formed file.

For a 2-day project, this is enough to show engineering hygiene without
needing to mock the entire Anthropic/Tavily SDKs.
"""

import os
import shutil
import pytest
from datetime import datetime, timezone

from src.schemas import ResearchPlan, ReflectionDecision, ResearchReport
from src.report_writer import save_report, OUTPUT_DIR


def test_research_plan_valid():
    plan = ResearchPlan(
        topic="Test topic",
        sub_questions=["Question 1?", "Question 2?"],
        reasoning="Because these cover the topic well.",
    )
    assert plan.topic == "Test topic"
    assert len(plan.sub_questions) == 2


def test_research_plan_rejects_too_many_sub_questions():
    with pytest.raises(Exception):
        ResearchPlan(
            topic="Test topic",
            sub_questions=[f"Q{i}?" for i in range(10)],  # exceeds max_length=6
            reasoning="Too many.",
        )


def test_reflection_decision_defaults():
    decision = ReflectionDecision(has_enough_information=True)
    assert decision.has_enough_information is True
    assert decision.missing_information is None
    assert decision.follow_up_query is None


def test_save_report_writes_file_and_cleans_up():
    report = ResearchReport(
        topic="Unit Test Topic",
        generated_at=datetime.now(timezone.utc),
        sub_questions=["Q1?"],
        summary="A short summary.",
        full_report_markdown="# Report\n\nSome content here.",
        sources=["https://example.com"],
        search_rounds=1,
    )

    filepath = save_report(report)
    try:
        assert os.path.exists(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Unit Test Topic" in content
        assert "Some content here." in content
    finally:
        # Clean up test artifact so it doesn't pollute outputs/reports/
        if os.path.exists(filepath):
            os.remove(filepath)
