"""
automation/scheduled_runner.py
-------------------------------
This is the "automation" piece of the project: a script with no human
in the loop. It reads a list of topics from config/topics.yaml, runs the
full agent on each one, and saves reports to disk.

This is meant to be triggered by a scheduler -- either a GitHub Actions
cron job (see .github/workflows/scheduled_research.yml) or a local cron
job / Windows Task Scheduler entry. The point is to demonstrate that the
agent isn't just an interactive toy -- it can run unattended as part of
a pipeline, which is how agentic systems are actually used in production
(e.g. a daily competitor-monitoring agent, a weekly industry digest, etc.).

Run manually with:
    python -m automation.scheduled_runner
"""

import sys
import yaml
from dotenv import load_dotenv

load_dotenv()

from src.agent import run_research_agent_sync
from src.report_writer import save_report

TOPICS_CONFIG_PATH = "config/topics.yaml"


def load_topics(path: str = TOPICS_CONFIG_PATH) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("topics", [])


def main():
    topics = load_topics()
    if not topics:
        print("No topics found in config/topics.yaml. Nothing to do.")
        return

    print(f"Running scheduled research on {len(topics)} topic(s)...\n")

    results = []
    for i, topic in enumerate(topics, 1):
        print(f"[{i}/{len(topics)}] Researching: {topic}")
        try:
            report = run_research_agent_sync(topic)
            path = save_report(report)
            print(f"    -> saved to {path}\n")
            results.append((topic, path, None))
        except Exception as e:
            print(f"    -> FAILED: {e}\n")
            results.append((topic, None, str(e)))

    # Summary, useful for CI logs
    print("\n=== Run Summary ===")
    for topic, path, error in results:
        status = f"OK -> {path}" if error is None else f"FAILED -> {error}"
        print(f"- {topic}: {status}")

    if any(error for _, _, error in results):
        sys.exit(1)  # non-zero exit so CI marks the run as failed if anything broke


if __name__ == "__main__":
    main()
