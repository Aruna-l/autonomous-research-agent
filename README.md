# 🔎 Autonomous Research Agent

An agentic AI research assistant that autonomously transforms a broad research
topic into a structured, grounded, and cited research report.

The system follows an iterative workflow:

**Plan → Search → Reflect → Search Again if Needed → Synthesize**

Instead of relying on a single LLM prompt, the application separates research
into multiple stages. The LLM generates focused sub-questions, web search is
performed through Tavily, the collected information is evaluated through a
reflection step, and the final evidence is synthesized into a Markdown report.

The project demonstrates practical **agentic AI architecture**, including
task decomposition, tool use, structured LLM outputs, reflection loops,
grounding, API orchestration, automated execution, and report generation.

---

## ✨ Features

- 🧠 **Autonomous task decomposition**
  - Converts a broad research topic into focused sub-questions.

- 🔎 **Web research using Tavily**
  - Searches the web for information relevant to each sub-question.

- 🔄 **Reflection loop**
  - Evaluates whether the collected research is sufficient.
  - Can trigger another research round when more information is required.

- 🤖 **LLM-powered synthesis**
  - Uses Gemini to synthesize collected research into a structured report.

- 📚 **Grounded research**
  - Final reports are generated from information collected through the search
    stage rather than from an isolated model response.

- 🧩 **Structured outputs**
  - Uses Gemini structured JSON responses for important agent stages.

- ✅ **Pydantic validation**
  - Agent outputs are validated against explicit schemas.

- 🌐 **FastAPI backend**
  - Exposes the research agent through HTTP endpoints.

- 🖥️ **Streamlit frontend**
  - Provides an interactive interface for running research and viewing results.

- 📡 **Live research streaming**
  - Progress from the backend can be streamed to the frontend.

- ⚙️ **Scheduled research**
  - Supports unattended research through GitHub Actions.

- 📄 **Markdown report generation**
  - Research results can be saved and downloaded as Markdown files.

- 🧪 **Automated tests**
  - Includes tests for schemas, report generation, and agent functionality.

---

# 🧠 What Makes This an Agent?

A basic LLM application often looks like:

```text
User
  │
  ▼
LLM
  │
  ▼
Answer

This project instead uses an agentic workflow:

                 ┌───────────────┐
                 │ Research Topic│
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │     PLAN      │
                 │    Gemini     │
                 │               │
                 │ Generate      │
                 │ sub-questions │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │     SEARCH    │
                 │    Tavily     │
                 │               │
                 │ Research each │
                 │ sub-question  │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │    REFLECT    │
                 │    Gemini     │
                 │               │
                 │ Is research   │
                 │ sufficient?   │
                 └───────┬───────┘
                         │
                    ┌────┴────┐
                    │         │
                   NO        YES
                    │         │
                    ▼         ▼
             ┌───────────┐ ┌───────────────┐
             │ Search    │ │   SYNTHESIZE  │
             │ Again     │ │    Gemini     │
             └─────┬─────┘ │               │
                   │       │ Final Report  │
                   └──────►└───────┬───────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │ Markdown Report  │
                         └──────────────────┘

The agent is not simply generating an answer. It performs multiple stages of
work and uses the output of one stage to determine what happens next.

The reflection/search loop is intentionally bounded to two research rounds
to provide an execution guardrail and prevent uncontrolled API usage.

🏗️ Architecture
┌───────────────────────────────┐
│        Streamlit UI           │
│                               │
│  Enter Topic → Run Research   │
└───────────────┬───────────────┘
                │ HTTP
                ▼
┌───────────────────────────────┐
│          FastAPI              │
│                               │
│ /research                     │
│ /research/stream              │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│        Research Agent         │
│                               │
│ Plan → Search → Reflect       │
│          ↘      ↗             │
│        Search Again            │
│               ↓               │
│           Synthesize           │
└────────────┬───────┬──────────┘
             │       │
             ▼       ▼
       ┌─────────┐ ┌──────────┐
       │ Gemini  │ │  Tavily  │
       │   API   │ │   API    │
       └─────────┘ └──────────┘
             │       │
             └───┬───┘
                 ▼
       ┌────────────────────┐
       │  Structured Report │
       │                    │
       │ Markdown + Sources │
       └────────────────────┘
🧰 Technology Stack
Component	Technology	Purpose
Programming Language	Python	Application and agent orchestration
LLM	Google Gemini API	Planning, reflection, and synthesis
Search	Tavily API	Web research
Backend	FastAPI	HTTP API
Frontend	Streamlit	Interactive UI
Validation	Pydantic	Structured data validation
Automation	GitHub Actions	Scheduled research
Configuration	YAML	Scheduled research topics
Testing	Pytest	Automated testing
Reports	Markdown	Research output
📁 Project Structure
autonomous-research-agent/
│
├── .github/
│   └── workflows/
│       └── scheduled_research.yml
│
├── api/
│   └── main.py
│
├── automation/
│   └── scheduled_runner.py
│
├── config/
│   └── topics.yaml
│
├── frontend/
│   └── app.py
│
├── outputs/
│   └── reports/
│       └── .gitkeep
│
├── src/
│   ├── __init__.py
│   ├── agent.py
│   ├── llm_client.py
│   ├── report_writer.py
│   ├── schemas.py
│   └── tools.py
│
├── tests/
│   └── test_agent.py
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
🔬 Core Components
1. src/agent.py

This is the core orchestration layer.

It coordinates the complete research workflow:

Topic
  ↓
Planning
  ↓
Search
  ↓
Reflection
  ↓
Additional Search (if required)
  ↓
Synthesis
  ↓
Research Report

The agent is responsible for controlling the sequence of operations and
passing structured information between stages.

2. src/llm_client.py

Provides the interface to the Gemini API.

Gemini is used for:

Research planning
Sub-question generation
Reflection decisions
Final report synthesis

Structured JSON output is used for agent stages where predictable data is
required.

This allows the rest of the application to work with validated structures
instead of depending on fragile free-form text parsing.

3. src/tools.py

Contains the Tavily web-search integration.

The search functionality is kept separate from the main agent orchestration so
that:

Agent
  │
  └── decides what information is needed
            │
            ▼
       Search Tool
            │
            ▼
      Tavily Web Search

This separation makes the search functionality easier to test and replace.

4. src/schemas.py

Defines the Pydantic models used throughout the application.

Schemas provide structured representations for important stages such as:

ResearchPlan
ReflectionDecision
ResearchReport
ResearchResponse

Validation helps prevent malformed LLM output from propagating through the
application.

5. src/report_writer.py

Responsible for converting completed research into persistent report files.

Reports are stored under:

outputs/reports/

The output format is Markdown, making reports easy to read, version, edit, or
convert to other formats.

6. api/main.py

Provides the FastAPI application.

The backend acts as the interface between the frontend and the agent.

Streamlit
    │
    ▼
FastAPI
    │
    ▼
Research Agent

This keeps the frontend thin and prevents it from directly owning the
agent orchestration logic.

7. frontend/app.py

Provides the Streamlit interface.

The frontend allows users to:

Enter a research topic
Start the research process
Observe research progress
View the generated report
Inspect collected sources
Download the report as Markdown

The frontend communicates with the FastAPI backend rather than running the
agent directly.

8. automation/scheduled_runner.py

Provides an unattended execution mode.

It reads research topics from:

config/topics.yaml

and executes the research agent for each configured topic.

This enables the project to operate as a scheduled research pipeline.

🔎 Example Research Flow

Suppose the user enters:

What are the major cybersecurity threats to small businesses in 2026,
and what practical measures can they take to reduce their risk?
Step 1 — Planning

Gemini decomposes the topic into focused questions such as:

1. What are the major emerging cybersecurity threats?
2. Why are small businesses common targets?
3. What vulnerabilities are frequently exploited?
4. What security controls provide the greatest risk reduction?
Step 2 — Search

Tavily searches the web for each research question.

The results are collected as research evidence.

Step 3 — Reflection

Gemini evaluates the collected information.

Conceptually:

Is the research sufficient?

        │
   ┌────┴────┐
   │         │
  YES        NO
   │         │
   ▼         ▼
Synthesize  Search Again
Step 4 — Synthesis

Gemini combines the collected information into a final report.

Step 5 — Output

The system produces a Markdown report containing the research findings and
sources.

📊 Report Output

A generated report contains information such as:

Research Topic
       │
       ├── Generated Sub-Questions
       │
       ├── Search Rounds
       │
       ├── Sources
       │
       ├── Executive Summary
       │
       ├── Detailed Findings
       │
       └── Recommendations

Reports are saved under:

outputs/reports/

The Streamlit frontend also provides a download option for the generated
Markdown report.

🌐 API Endpoints
GET /

Basic root endpoint for the FastAPI application.

POST /research

Runs a complete research task.

Example request:

{
  "topic": "What are the major cybersecurity threats to small businesses in 2026?"
}

The endpoint returns a structured research response containing the generated
report and associated research information.

GET /research/stream

Runs research while streaming progress events.

The streaming endpoint allows clients to receive updates while the agent is
working instead of waiting for the entire process to finish.

Example progress flow:

Starting research...
        ↓
Planning research questions...
        ↓
Searching for information...
        ↓
Evaluating research...
        ↓
Performing additional research...
        ↓
Synthesizing report...
        ↓
Research complete
🖥️ Running the Application
Prerequisites

Install:

Python 3.11+
Git
Gemini API key
Tavily API key
🚀 Installation
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd autonomous-research-agent
2. Create a virtual environment
Windows
python -m venv venv
venv\Scripts\activate
macOS / Linux
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
🔐 Environment Configuration

Create a .env file in the project root.

You can start from:

.env.example

Example:

GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

If model configuration is supported by your current implementation, it can also
be specified through an environment variable.

For example:

GEMINI_MODEL=gemini-3.6-flash
⚠️ Security

Never commit .env to GitHub.

API keys must remain private.

The repository includes .gitignore to prevent local environment files and
other sensitive/local files from being committed.

🔑 Obtaining API Keys
Gemini

Create a Gemini API key through Google AI Studio.

Store the key in:

GEMINI_API_KEY=your_key_here
Tavily

Create a Tavily API key through Tavily.

Store it in:

TAVILY_API_KEY=your_key_here

Do not hard-code either key directly into the source code.

▶️ Run the Backend

From the project root:

uvicorn api.main:app --reload

The API will start at:

http://127.0.0.1:8000

Open the interactive FastAPI documentation:

http://127.0.0.1:8000/docs

The Swagger interface can be used to test the research API directly.

🖥️ Run the Frontend

Open a second terminal.

Activate the virtual environment if necessary:

Windows
venv\Scripts\activate

Then run:

streamlit run frontend/app.py

The Streamlit application will open in your browser.

The frontend communicates with:

http://127.0.0.1:8000

by default.

⚙️ Scheduled Research

Research topics can be configured in:

config/topics.yaml

The scheduled runner can be executed manually using:

python -m automation.scheduled_runner

The project also contains a GitHub Actions workflow:

.github/workflows/scheduled_research.yml

This allows research jobs to be executed automatically according to the
configured workflow schedule.

🧪 Testing

Run the test suite with:

pytest tests/ -v

The tests cover important application components including schema validation
and report-writing functionality.

🧩 Agentic AI Concepts Demonstrated
Concept	How It Is Implemented
Task Decomposition	Broad research topic is converted into sub-questions
Tool Use	Tavily is used as an external search tool
Reflection	Gemini evaluates whether additional research is needed
Iterative Execution	Agent can perform an additional research round
Grounding	Synthesis is based on collected search results
Structured Generation	Gemini structured JSON output
Validation	Pydantic models validate agent outputs
Orchestration	Python coordinates the agent stages
Streaming	FastAPI exposes live research progress
Automation	GitHub Actions supports scheduled execution
Artifact Generation	Research is saved as Markdown reports
🏛️ Design Principles
Separation of Concerns

The project separates the system into independent layers:

Frontend
   │
   ▼
API
   │
   ▼
Agent
   │
   ├──────────► Gemini
   │
   └──────────► Tavily

The frontend does not directly run the research agent.

The FastAPI backend owns the orchestration.

Structured Data

Important agent outputs are represented using Pydantic schemas.

Instead of relying on:

"Here is some text that looks like JSON..."

the application expects structured data matching predefined models.

This improves reliability and makes downstream processing easier.

Bounded Autonomy

The agent can decide whether another search round is useful, but autonomous
execution is still bounded.

The research loop is capped at:

Maximum research rounds = 2

This provides a practical guardrail for execution time and API usage.

🔄 End-to-End Workflow
                         USER
                           │
                           ▼
                    Research Topic
                           │
                           ▼
                    ┌────────────┐
                    │   PLAN     │
                    │   Gemini   │
                    └─────┬──────┘
                          │
                          ▼
                 Generate Sub-Questions
                          │
                          ▼
                    ┌────────────┐
                    │   SEARCH   │
                    │   Tavily   │
                    └─────┬──────┘
                          │
                          ▼
                  Collect Search Results
                          │
                          ▼
                    ┌────────────┐
                    │  REFLECT   │
                    │   Gemini   │
                    └─────┬──────┘
                          │
                    ┌─────┴─────┐
                    │           │
                   NO          YES
                    │           │
                    ▼           │
               Search Again     │
                    │           │
                    └─────┬─────┘
                          │
                          ▼
                    ┌────────────┐
                    │ SYNTHESIZE │
                    │   Gemini   │
                    └─────┬──────┘
                          │
                          ▼
                 Grounded Markdown
                      Report
                          │
                 ┌────────┴────────┐
                 ▼                 ▼
             Streamlit         File Output
                UI             Markdown
📈 Why This Project Is Different From a Basic LLM Wrapper

A simple LLM wrapper generally performs:

Prompt → LLM → Response

This project introduces an explicit workflow around the LLM:

Problem
  ↓
Decomposition
  ↓
External Information Gathering
  ↓
Evaluation
  ↓
Iterative Research
  ↓
Evidence-Based Synthesis
  ↓
Report

The LLM is therefore one component of a larger system rather than the entire
application.

The project focuses on orchestration and agent behavior, not only prompt
generation.

🔐 Reliability and Safety Considerations

The current architecture includes several controls:

Bounded research

The reflection loop is capped to a maximum number of research rounds.

Schema validation

Pydantic validates structured agent outputs.

Environment-based secrets

API keys are loaded through environment variables.

Separation of frontend and backend

The UI does not directly own the agent's orchestration logic.

Deterministic search execution

The search tool is explicitly invoked by the agent workflow for the generated
research questions.

📦 Example Commands
Start API
uvicorn api.main:app --reload
Start UI
streamlit run frontend/app.py
Run scheduled research
python -m automation.scheduled_runner
Run tests
pytest tests/ -v
🛠️ Future Improvements

Possible future extensions include:

 Parallel research for independent sub-questions
 Source quality scoring
 Source deduplication
 Citation verification
 Research history
 Persistent database storage
 PDF report generation
 Configurable research depth
 Configurable maximum search rounds
 Additional search providers
 Additional LLM providers
 Report comparison across research runs
 Improved source attribution
 Research dashboard and analytics
 User authentication
 Multi-user research workspaces
📌 Example Use Cases

The agent can be used for research topics across multiple domains, including:

Cybersecurity
What are the major ransomware trends affecting organizations in 2026?
Technology
What are the most important developments in AI infrastructure in 2026?
Business
What factors are driving the growth of AI startups?
Research
What are the latest developments in autonomous AI agents?
Market Research
What are the major trends shaping the cybersecurity industry?

The system is domain-agnostic: the topic is supplied by the user and the agent
determines the research questions required to investigate it.

📚 Learning Objectives

This project was built to explore and demonstrate:

Agentic AI architecture
LLM orchestration
Task decomposition
Function/tool calling concepts
Web research pipelines
Reflection-based workflows
Structured LLM generation
Pydantic validation
FastAPI API design
Streamlit application development
Streaming responses
Automated workflows
GitHub Actions
AI-generated research artifacts
🗺️ Project Roadmap
                CURRENT
                   │
                   ▼
       ┌──────────────────────┐
       │ Plan → Search →      │
       │ Reflect → Synthesize │
       └──────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │ Better source        │
       │ evaluation           │
       └──────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │ Citation verification│
       └──────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │ Persistent research  │
       │ history              │
       └──────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │ Advanced research    │
       │ workflows             │
       └──────────────────────┘
🤝 Contributing

Contributions, ideas, and improvements are welcome.

A typical contribution workflow:

git clone <repository-url>

cd autonomous-research-agent

git checkout -b feature/my-feature

# Make your changes

pytest tests/ -v

git add .

git commit -m "Add my feature"

git push origin feature/my-feature

Then open a Pull Request on GitHub.

⚠️ Limitations

This project is intended as an exploration of agentic research workflows and
should not be treated as a replacement for professional research or expert
verification.

Web search results can contain:

outdated information
incomplete information
conflicting sources
inaccurate claims
low-quality sources

The agent can improve the research workflow, but generated reports should
still be reviewed when accuracy is important.

📄 License

This project is released under the MIT License.

See the LICENSE file for details.

👤 Author

Autonomous Research Agent

Built as a practical exploration of:

Agentic AI · LLM Orchestration · Tool Use · Web Research · Reflection ·
Grounded Generation · FastAPI · Streamlit · Automation



