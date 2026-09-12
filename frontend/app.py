"""
frontend/app.py
----------------
Streamlit UI for the research agent.

Talks to the FastAPI backend (does NOT call the agent directly).

Run with:
    streamlit run frontend/app.py
"""

import json
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Autonomous Research Agent",
    page_icon="🔎",
    layout="centered",
)

st.title("🔎 Autonomous Research Agent")
st.caption("Plan → Search → Reflect → Synthesize, powered by Gemini + Tavily")


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "final_report" not in st.session_state:
    st.session_state.final_report = None

if "research_topic" not in st.session_state:
    st.session_state.research_topic = ""


# ---------------------------------------------------------
# Input
# ---------------------------------------------------------

topic = st.text_input(
    "Research topic",
    placeholder="e.g. Impact of tariffs on semiconductor supply chains",
)

run_clicked = st.button(
    "Run Research",
    type="primary",
    disabled=not topic.strip(),
)


# ---------------------------------------------------------
# Run research
# ---------------------------------------------------------

if run_clicked:

    # Clear previous report only when starting a NEW research run
    st.session_state.final_report = None
    st.session_state.research_topic = topic

    progress_container = st.container()
    progress_lines = []
    final_report = None

    with progress_container:

        status_box = st.status(
            "Starting agent...",
            expanded=True,
        )

        try:

            with requests.get(
                f"{API_URL}/research/stream",
                params={"topic": topic},
                stream=True,
                timeout=300,
            ) as response:

                response.raise_for_status()

                for raw_line in response.iter_lines(
                    decode_unicode=True
                ):

                    if not raw_line or not raw_line.startswith("data: "):
                        continue

                    event = json.loads(
                        raw_line[len("data: "):]
                    )

                    if event["type"] == "progress":

                        progress_lines.append(
                            event["message"]
                        )

                        status_box.write(
                            event["message"]
                        )

                    elif event["type"] == "done":

                        final_report = event["report"]

                        # Store the report permanently
                        # for this Streamlit session
                        st.session_state.final_report = final_report

                        status_box.update(
                            label="Done!",
                            state="complete",
                            expanded=False,
                        )

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not reach the API. Make sure it's running:\n\n"
                "`uvicorn api.main:app --reload`"
            )

        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )


# ---------------------------------------------------------
# Display saved research report
# ---------------------------------------------------------

if st.session_state.final_report:

    final_report = st.session_state.final_report

    st.divider()

    st.subheader(
        f"Report: {final_report['topic']}"
    )

    st.caption(
        f"Sub-questions: {len(final_report['sub_questions'])} · "
        f"Search rounds: {final_report['search_rounds']} · "
        f"Sources: {len(final_report['sources'])}"
    )

    # Main report
    st.markdown(
        final_report["full_report_markdown"]
    )

    # Sources
    with st.expander("Sources"):

        for url in final_report["sources"]:

            st.markdown(
                f"- {url}"
            )

    # Download
    st.download_button(
        "Download report as markdown",
        data=final_report["full_report_markdown"],
        file_name=(
            f"{final_report['topic'][:40].replace(' ', '_')}.md"
        ),
        mime="text/markdown",
    )