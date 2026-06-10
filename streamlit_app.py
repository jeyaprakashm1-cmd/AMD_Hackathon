"""
AI Interview Evaluation System - Phase 1
Streamlit Application Entry Point

Module 1: Project setup and folder structure.
Detailed pages and business logic will be added module by module.
"""

import streamlit as st


APP_TITLE = "AI Interview Evaluation System"
APP_VERSION = "Phase 1 - Module 1"


DEFAULT_SESSION_STATE = {
    "jd_id": None,
    "candidate_id": None,
    "questions": [],
    "current_question_index": 0,
    "answers_saved": 0,
    "interview_completed": False,
    "evaluation_done": False,
    "report_id": None,
    "active_page": "Dashboard",
}


PAGES = [
    "Dashboard",
    "JD Analysis",
    "Resume Analysis",
    "Question Generation",
    "Interview",
    "Evaluation",
    "Report",
    "Analytics",
    "Logs",
    "Settings",
]


def initialize_session_state() -> None:
    """Initialize Streamlit session state keys required for the workflow."""
    for key, value in DEFAULT_SESSION_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar() -> str:
    """Render sidebar navigation and return selected page."""
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio(
        "Go to",
        PAGES,
        index=PAGES.index(st.session_state.get("active_page", "Dashboard")),
    )
    st.session_state["active_page"] = selected_page

    st.sidebar.markdown("---")
    st.sidebar.caption(APP_VERSION)
    return selected_page


def render_dashboard() -> None:
    """Render initial dashboard placeholder."""
    st.title(APP_TITLE)
    st.subheader("Workflow Status")

    col1, col2, col3 = st.columns(3)
    col1.metric("JD Status", "Done" if st.session_state.jd_id else "Pending")
    col2.metric("Candidate Status", "Done" if st.session_state.candidate_id else "Pending")
    col3.metric("Questions", len(st.session_state.questions))

    col4, col5, col6 = st.columns(3)
    col4.metric("Answers Saved", st.session_state.answers_saved)
    col5.metric("Interview", "Completed" if st.session_state.interview_completed else "Pending")
    col6.metric("Evaluation", "Done" if st.session_state.evaluation_done else "Pending")

    st.info(
        "Module 1 is ready: project structure, Streamlit entry point, "
        "session state contract, and navigation placeholders are configured."
    )


def render_placeholder_page(page_name: str) -> None:
    """Render placeholder for pages that will be implemented in later modules."""
    st.title(page_name)
    st.warning(f"{page_name} page will be implemented in upcoming modules.")


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    initialize_session_state()
    selected_page = render_sidebar()

    if selected_page == "Dashboard":
        render_dashboard()
    else:
        render_placeholder_page(selected_page)


if __name__ == "__main__":
    main()
