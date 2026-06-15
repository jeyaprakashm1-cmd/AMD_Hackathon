import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.title("AI Interviewer")

        page = st.radio(
            "Navigation",
            ["Dashboard", "Upload Resume", "Active Interview", "Results", "Settings"]
        )

    return page