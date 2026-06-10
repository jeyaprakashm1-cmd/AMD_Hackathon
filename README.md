# AI Interview Evaluation System

Phase 1 deploy-ready Streamlit application for AI-assisted interview evaluation using rule-based logic and SQLite.

## Tech Stack

- Python
- Streamlit
- SQLite
- pandas
- matplotlib / plotly
- Rule-based model logic for Phase 1

## Project Structure

```text
interview_system/
├── streamlit_app.py
├── database.py
├── models.py
├── agents.py
├── analytics.py
├── utils.py
├── requirements.txt
├── README.md
└── interview_system.db
```

## Module 1 Status

Implemented:

- Project folder structure
- Streamlit entry point
- Sidebar navigation placeholders
- Session state contract
- Utility placeholder functions
- Placeholder files for DB, model, agents, and analytics layers

## Run Locally

```bash
cd interview_system
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Phase 1 Workflow

1. JD Analysis
2. Resume Analysis
3. Question Generation
4. Interview
5. Evaluation
6. Report
7. Analytics
8. Logs
9. Settings

## Notes

- No external paid APIs are used.
- Rule-based logic is used in Phase 1.
- SQLite database implementation starts in Module 2.
