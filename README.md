# Autonomous Research Agent

An agentic research assistant that takes a broad topic, autonomously plans
sub-questions, searches the web, reflects on whether it has enough
information, and synthesizes a grounded, cited markdown report — with no
human in the loop after the initial prompt.

Built to demonstrate core agentic AI concepts: **tool/function calling**,
**task decomposition**, **self-reflection loops**, **grounding**, and
**automation**, on top of the Gemini API.

## Why this exists

This isn't a wrapper around a single API call. It's a genuine **agent
loop** — the model itself decides how many search rounds it needs and
when it has enough information, within guardrails set by the code.

```
   ┌─────────┐     ┌────────┐     ┌───────────┐     ┌──────────────┐
   │  PLAN   │ ──▶ │ SEARCH │ ──▶ │  REFLECT  │ ──▶ │  SYNTHESIZE  │
   │ (Gemini)│     │(Tavily)│     │  (Gemini) │     │   (Gemini)   │
   └─────────┘     └────────┘     └─────┬─────┘     └──────────────┘
                        ▲               │
                        │  not enough?  │
                        └───────────────┘
                     (capped at 2 rounds)
```

## Architecture

| Layer | Tech | Purpose |
|---|---|---|
| LLM | Gemini API (Google) | Planning, reflection, synthesis — via native structured JSON output (`response_schema`) |
| Search tool | Tavily API | LLM-optimized web search, called deterministically per sub-question |
| Backend | FastAPI | Exposes the agent as an HTTP API (`/research`, `/research/stream`) |
| Frontend | Streamlit | Live view of the agent's reasoning as it runs, not just a final blob |
| Automation | GitHub Actions (cron) | Runs the agent unattended on a list of topics on a schedule |
| Validation | Pydantic | Every step's output is schema-validated, not loosely parsed text |

## Project structure

```
autonomous-research-agent/
├── src/
│   ├── schemas.py        # Pydantic models for every step's output
│   ├── tools.py           # Tavily search tool + its LLM tool schema
│   ├── llm_client.py       # Gemini API calls (native structured JSON output)
│   ├── agent.py             # THE CORE LOOP: plan → search → reflect → synthesize
│   └── report_writer.py     # Saves reports to outputs/reports/
├── api/main.py                # FastAPI app
├── frontend/app.py             # Streamlit UI
├── automation/scheduled_runner.py  # Unattended batch runner
├── config/topics.yaml               # Topics for scheduled runs
└── tests/test_agent.py               # Schema + report-writer tests
```

## Setup

```bash
git clone <your-repo-url>
cd autonomous-research-agent
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env   # then fill in your GEMINI_API_KEY and TAVILY_API_KEY
```

Get free API keys:
- Gemini: https://aistudio.google.com/apikey (free tier, no card required)
- Tavily: https://tavily.com (1,000 free searches/month, no card required)

## Running it

**1. Start the backend API:**
```bash
uvicorn api.main:app --reload
```
Visit `http://127.0.0.1:8000/docs` for the interactive API playground.

**2. Start the frontend (in a separate terminal, API must be running):**
```bash
streamlit run frontend/app.py
```

**3. Or run a one-off batch of topics with no UI at all:**
```bash
python -m automation.scheduled_runner
```

**4. Run the tests:**
```bash
pytest tests/ -v
```

## Design decisions worth knowing for a walkthrough

- **Structured outputs via native JSON mode.** Gemini's `response_schema`
  parameter accepts a Pydantic model directly, so planning and reflection
  steps get an already-validated object back (`response.parsed`) instead
  of free text we'd have to parse ourselves. Guarantees the agent loop
  always gets reliable, typed data.
- **Reflection is capped at 2 rounds.** An agent that can loop forever is
  a cost and reliability risk. The cap is a deliberate guardrail, not an
  oversight.
- **Search is deterministic, not model-triggered, for the initial round.**
  Each sub-question gets exactly one search — this keeps the first pass
  fast and predictable. The *reflection* step is where the model gets
  real agency: it decides whether another search is warranted at all.
- **No LangChain/LangGraph.** Built directly on the Gemini SDK so every
  part of the loop is transparent and explainable — a deliberate choice
  to demonstrate understanding of the underlying mechanics before
  reaching for a framework abstraction.
- **Grounding.** The synthesis prompt explicitly forbids using outside
  knowledge — the report can only state what the search results actually
  contain, which is the core idea behind reducing hallucination in
  production LLM systems.

## Known limitations (good interview talking points, not hidden flaws)

- `/research` runs synchronously — a production version would use a job
  queue for long-running agent runs instead of blocking the request.
- Search results aren't deduplicated across sub-questions/rounds.
- No conversation memory across separate research runs (each run is
  stateless by design, to keep scope tight).
