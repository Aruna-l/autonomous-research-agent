"""
api/main.py
-----------
Exposes the research agent as an HTTP API using FastAPI.

Why wrap it in an API at all? Because a real agent is rarely used by
typing into a terminal -- it gets called by other systems, a frontend,
a scheduler, or another service. This file is the "front door" that
turns your agent function into something other software can trigger.

Run with:
    uvicorn api.main:app --reload

Then visit http://127.0.0.1:8000/docs for interactive Swagger UI.
"""

import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()  # loads .env before anything tries to read API keys

from src.agent import run_research_agent_sync, run_research_agent
from src.report_writer import save_report
from src.schemas import ResearchReport

app = FastAPI(
    title="Autonomous Research Agent API",
    description="POST a topic, get back a grounded, cited research report.",
    version="1.0.0",
)


class ResearchRequest(BaseModel):
    topic: str


class ResearchResponse(BaseModel):
    report: ResearchReport
    saved_path: str


@app.get("/")
def root():
    return {"status": "ok", "message": "Autonomous Research Agent API is running."}


@app.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest):
    """
    Runs the full agent loop synchronously and returns the finished report.
    For a real production system you'd likely make this async / job-queued,
    since agent runs can take 30-90 seconds -- noted here deliberately as
    a known simplification, worth mentioning if asked in an interview.
    """
    if not request.topic or not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic must not be empty.")

    try:
        report = run_research_agent_sync(request.topic)
        saved_path = save_report(report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent run failed: {e}")

    return ResearchResponse(report=report, saved_path=saved_path)


@app.get("/research/stream")
def research_stream(topic: str):
    """
    Same agent run as /research, but streams progress line-by-line as
    Server-Sent Events (SSE) so a frontend can show live status instead
    of a blank spinner for 30-90 seconds. The final event contains the
    complete ResearchReport as JSON.
    """
    if not topic or not topic.strip():
        raise HTTPException(status_code=400, detail="Topic must not be empty.")

    def event_generator():
        gen = run_research_agent(topic)
        report = None
        try:
            while True:
                progress_line = next(gen)
                yield f"data: {json.dumps({'type': 'progress', 'message': progress_line})}\n\n"
        except StopIteration as stop:
            report = stop.value

        if report is not None:
            saved_path = save_report(report)
            payload = {
                "type": "done",
                "report": json.loads(report.model_dump_json()),
                "saved_path": saved_path,
            }
            yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
