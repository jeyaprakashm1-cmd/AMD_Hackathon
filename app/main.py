from app.ui.components.sidebar import render_sidebar

from app.ui.pages.dashboard import show_dashboard
from app.ui.pages.resume_upload import show_resume_upload
from app.ui.pages.interview import show_interview
from app.ui.pages.evaluation import show_results
from app.ui.pages.settings import show_settings

# Get selected page
page = render_sidebar()

# Routing logic
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