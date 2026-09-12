"""
report_writer.py
-----------------
Small utility: takes a ResearchReport and writes it to disk as a markdown
file, with a filename based on the topic and timestamp. Kept separate from
agent.py so the agent's core logic doesn't need to know about the filesystem
-- it just produces a ResearchReport object, and this module decides what
to do with it (save to disk, but could just as easily be "email it" or
"post it to Slack" later).
"""

import re
import os
from src.schemas import ResearchReport

OUTPUT_DIR = os.path.join("outputs", "reports")


def _slugify(text: str, max_len: int = 50) -> str:
    """Turns a topic string into a safe filename fragment."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug[:max_len]


def save_report(report: ResearchReport) -> str:
    """
    Writes the report to outputs/reports/<slug>_<timestamp>.md
    Returns the file path written.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
    filename = f"{_slugify(report.topic)}_{timestamp}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    header = (
        f"# Research Report: {report.topic}\n\n"
        f"*Generated: {report.generated_at.isoformat()} UTC*  \n"
        f"*Search rounds: {report.search_rounds}*  \n"
        f"*Sub-questions: {len(report.sub_questions)}*\n\n"
        f"---\n\n"
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(report.full_report_markdown)

    return filepath
