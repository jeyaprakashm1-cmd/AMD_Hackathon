import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.title("🤖 AI Interviewer")

        st.markdown("---")

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Upload Resume",
                "Active Interview",
                "Results",
                "Settings"
            ]
        )

        st.markdown("---")
        st.caption("AI Interview Platform v1.0")

    return page