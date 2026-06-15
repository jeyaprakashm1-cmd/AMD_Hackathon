import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.title("AI Interviewer")

        st.page_link("app/main.py", label="Dashboard")
        st.page_link("app/pages/upload.py", label="Upload Resume")
        st.page_link("app/pages/interview.py", label="Active Interview")
        st.page_link("app/pages/results.py", label="Results")
        st.page_link("app/pages/settings.py", label="Settings")