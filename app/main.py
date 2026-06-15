import streamlit as st

# Import sidebar
from ui.components.sidebar import render_sidebar

# Import pages
from ui.pages.dashboard import show_dashboard
from ui.pages.resume_upload import show_resume_upload
from ui.pages.interview import show_interview
from ui.pages.evaluation import show_results
from ui.pages.settings import show_settings


# ✅ Page configuration (important)
st.set_page_config(
    page_title="AI Interviewer",
    layout="wide"
)


# ✅ Render sidebar and get selected page
page = render_sidebar()


# ✅ Routing logic (centralized navigation)
if page == "Dashboard":
    show_dashboard()

elif page == "Upload Resume":
    show_resume_upload()

elif page == "Active Interview":
    show_interview()

elif page == "Results":
    show_results()

elif page == "Settings":
    show_settings()

else:
    # fallback (safety)
    show_dashboard()