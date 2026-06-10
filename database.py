"""
SQLite database layer for AI Interview Evaluation System.

Module 2:
- SQLite connection management
- Table creation
- Basic CRUD helpers
- Required Phase 1 tables
- Initial audit/model log helper methods

Database file:
    interview_system.db
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import json


DB_NAME = "interview_system.db"


def current_timestamp() -> str:
    """Return current timestamp as string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def to_json(data: Any) -> str:
    """Safely convert Python object to JSON string."""
    try:
        return json.dumps(data, ensure_ascii=False, default=str)
    except Exception:
        return "{}"


def from_json(data: Optional[str], default: Any = None) -> Any:
    """Safely convert JSON string to Python object."""
    if default is None:
        default = {}
    if not data:
        return default
    try:
        return json.loads(data)
    except Exception:
        return default


class DatabaseManager:
    """
    Database manager for the AI Interview Evaluation System.

    This class owns:
    - SQLite connection creation
    - Schema initialization
    - Insert/update/fetch helpers
    - Audit logs
    - Model execution logs
    """

    def __init__(self, db_path: str = DB_NAME):
        self.db_path = Path(db_path)

    def connect(self) -> sqlite3.Connection:
        """
        Create SQLite connection.

        row_factory allows query results to be accessed like dictionaries.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(
        self,
        query: str,
        params: Tuple[Any, ...] = (),
        commit: bool = True,
    ) -> int:
        """
        Execute INSERT/UPDATE/DELETE query.

        Returns:
            Last inserted row id for insert operations.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()
            return cursor.lastrowid

    def fetch_all(
        self,
        query: str,
        params: Tuple[Any, ...] = (),
    ) -> List[Dict[str, Any]]:
        """Fetch all records as list of dictionaries."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def fetch_one(
        self,
        query: str,
        params: Tuple[Any, ...] = (),
    ) -> Optional[Dict[str, Any]]:
        """Fetch one record as dictionary."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    def initialize_database(self) -> None:
        """Initialize all required database tables."""
        self.create_tables()

    def create_tables(self) -> None:
        """Create all required Phase 1 tables."""
        with self.connect() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS job_descriptions (
                    jd_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_title TEXT NOT NULL,
                    job_description TEXT NOT NULL,
                    extracted_skills_json TEXT,
                    experience_level TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS candidates (
                    candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_name TEXT NOT NULL,
                    resume_text TEXT NOT NULL,
                    extracted_skills_json TEXT,
                    experience_years INTEGER DEFAULT 0,
                    matched_skills_json TEXT,
                    missing_skills_json TEXT,
                    match_percentage REAL DEFAULT 0,
                    jd_id INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    FOREIGN KEY (jd_id) REFERENCES job_descriptions (jd_id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS interview_questions (
                    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jd_id INTEGER,
                    skill TEXT,
                    question_text TEXT NOT NULL,
                    question_type TEXT DEFAULT 'technical',
                    difficulty TEXT DEFAULT 'medium',
                    expected_keywords_json TEXT,
                    max_score REAL DEFAULT 10,
                    question_order INTEGER,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (jd_id) REFERENCES job_descriptions (jd_id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS candidate_answers (
                    answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    answer_text TEXT NOT NULL,
                    score REAL,
                    feedback TEXT,
                    matched_keywords_json TEXT,
                    missing_keywords_json TEXT,
                    created_at TEXT NOT NULL,
                    evaluated_at TEXT,
                    FOREIGN KEY (candidate_id) REFERENCES candidates (candidate_id),
                    FOREIGN KEY (question_id) REFERENCES interview_questions (question_id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS evaluation_reports (
                    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id INTEGER NOT NULL,
                    jd_id INTEGER NOT NULL,
                    technical_score REAL DEFAULT 0,
                    communication_score REAL DEFAULT 0,
                    overall_score REAL DEFAULT 0,
                    strengths_json TEXT,
                    weaknesses_json TEXT,
                    recommendation TEXT,
                    report_text TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (candidate_id) REFERENCES candidates (candidate_id),
                    FOREIGN KEY (jd_id) REFERENCES job_descriptions (jd_id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    event_description TEXT NOT NULL,
                    entity_type TEXT,
                    entity_id INTEGER,
                    metadata_json TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS model_execution_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    input_json TEXT,
                    output_json TEXT,
                    status TEXT DEFAULT 'success',
                    error_message TEXT,
                    execution_time_seconds REAL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )

            conn.commit()

    def clear_database(self) -> None:
        """
        Clear all application data.

        This is useful for Settings page reset/demo testing.
        """
        tables = [
            "candidate_answers",
            "evaluation_reports",
            "interview_questions",
            "candidates",
            "job_descriptions",
            "audit_logs",
            "model_execution_logs",
        ]

        with self.connect() as conn:
            cursor = conn.cursor()
            for table in tables:
                cursor.execute(f"DELETE FROM {table}")
            conn.commit()

    # ---------------------------------------------------------------------
    # Audit and model logs
    # ---------------------------------------------------------------------

    def insert_audit_log(
        self,
        event_type: str,
        event_description: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Insert audit log record."""
        query = """
            INSERT INTO audit_logs (
                event_type,
                event_description,
                entity_type,
                entity_id,
                metadata_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(
            query,
            (
                event_type,
                event_description,
                entity_type,
                entity_id,
                to_json(metadata or {}),
                current_timestamp(),
            ),
        )

    def insert_model_execution_log(
        self,
        model_name: str,
        task_type: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        execution_time_seconds: float = 0,
    ) -> int:
        """Insert model/rule execution log record."""
        query = """
            INSERT INTO model_execution_logs (
                model_name,
                task_type,
                input_json,
                output_json,
                status,
                error_message,
                execution_time_seconds,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(
            query,
            (
                model_name,
                task_type,
                to_json(input_data or {}),
                to_json(output_data or {}),
                status,
                error_message,
                execution_time_seconds,
                current_timestamp(),
            ),
        )

    # ---------------------------------------------------------------------
    # Insert methods
    # ---------------------------------------------------------------------

    def insert_job_description(
        self,
        job_title: str,
        job_description: str,
        extracted_skills: Optional[List[str]] = None,
        experience_level: Optional[str] = None,
    ) -> int:
        """Insert a job description."""
        query = """
            INSERT INTO job_descriptions (
                job_title,
                job_description,
                extracted_skills_json,
                experience_level,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """
        jd_id = self.execute_query(
            query,
            (
                job_title,
                job_description,
                to_json(extracted_skills or []),
                experience_level,
                current_timestamp(),
                current_timestamp(),
            ),
        )

        self.insert_audit_log(
            event_type="job_description_created",
            event_description=f"Job description created for {job_title}",
            entity_type="job_descriptions",
            entity_id=jd_id,
            metadata={"job_title": job_title},
        )

        return jd_id

    def insert_candidate(
        self,
        candidate_name: str,
        resume_text: str,
        jd_id: Optional[int] = None,
        extracted_skills: Optional[List[str]] = None,
        experience_years: int = 0,
        matched_skills: Optional[List[str]] = None,
        missing_skills: Optional[List[str]] = None,
        match_percentage: float = 0,
    ) -> int:
        """Insert candidate and resume analysis details."""
        query = """
            INSERT INTO candidates (
                candidate_name,
                resume_text,
                extracted_skills_json,
                experience_years,
                matched_skills_json,
                missing_skills_json,
                match_percentage,
                jd_id,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        candidate_id = self.execute_query(
            query,
            (
                candidate_name,
                resume_text,
                to_json(extracted_skills or []),
                experience_years,
                to_json(matched_skills or []),
                to_json(missing_skills or []),
                match_percentage,
                jd_id,
                current_timestamp(),
                current_timestamp(),
            ),
        )

        self.insert_audit_log(
            event_type="candidate_created",
            event_description=f"Candidate created: {candidate_name}",
            entity_type="candidates",
            entity_id=candidate_id,
            metadata={"candidate_name": candidate_name, "jd_id": jd_id},
        )

        return candidate_id

    def insert_interview_question(
        self,
        jd_id: int,
        skill: str,
        question_text: str,
        question_type: str = "technical",
        difficulty: str = "medium",
        expected_keywords: Optional[List[str]] = None,
        max_score: float = 10,
        question_order: Optional[int] = None,
    ) -> int:
        """Insert generated interview question."""
        query = """
            INSERT INTO interview_questions (
                jd_id,
                skill,
                question_text,
                question_type,
                difficulty,
                expected_keywords_json,
                max_score,
                question_order,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        question_id = self.execute_query(
            query,
            (
                jd_id,
                skill,
                question_text,
                question_type,
                difficulty,
                to_json(expected_keywords or []),
                max_score,
                question_order,
                current_timestamp(),
            ),
        )

        self.insert_audit_log(
            event_type="interview_question_created",
            event_description=f"Interview question created for skill: {skill}",
            entity_type="interview_questions",
            entity_id=question_id,
            metadata={"jd_id": jd_id, "skill": skill, "question_type": question_type},
        )

        return question_id

    def insert_candidate_answer(
        self,
        candidate_id: int,
        question_id: int,
        answer_text: str,
    ) -> int:
        """Insert candidate answer."""
        query = """
            INSERT INTO candidate_answers (
                candidate_id,
                question_id,
                answer_text,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """
        answer_id = self.execute_query(
            query,
            (
                candidate_id,
                question_id,
                answer_text,
                current_timestamp(),
            ),
        )

        self.insert_audit_log(
            event_type="candidate_answer_saved",
            event_description="Candidate answer saved",
            entity_type="candidate_answers",
            entity_id=answer_id,
            metadata={"candidate_id": candidate_id, "question_id": question_id},
        )

        return answer_id

    def insert_evaluation_report(
        self,
        candidate_id: int,
        jd_id: int,
        technical_score: float,
        communication_score: float,
        overall_score: float,
        strengths: Optional[List[str]] = None,
        weaknesses: Optional[List[str]] = None,
        recommendation: str = "Maybe",
        report_text: str = "",
    ) -> int:
        """Insert final evaluation report."""
        query = """
            INSERT INTO evaluation_reports (
                candidate_id,
                jd_id,
                technical_score,
                communication_score,
                overall_score,
                strengths_json,
                weaknesses_json,
                recommendation,
                report_text,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        report_id = self.execute_query(
            query,
            (
                candidate_id,
                jd_id,
                technical_score,
                communication_score,
                overall_score,
                to_json(strengths or []),
                to_json(weaknesses or []),
                recommendation,
                report_text,
                current_timestamp(),
            ),
        )

        self.insert_audit_log(
            event_type="evaluation_report_created",
            event_description="Evaluation report created",
            entity_type="evaluation_reports",
            entity_id=report_id,
            metadata={
                "candidate_id": candidate_id,
                "jd_id": jd_id,
                "overall_score": overall_score,
                "recommendation": recommendation,
            },
        )

        return report_id

    # ---------------------------------------------------------------------
    # Update methods
    # ---------------------------------------------------------------------

    def update_candidate_answer_evaluation(
        self,
        answer_id: int,
        score: float,
        feedback: str,
        matched_keywords: Optional[List[str]] = None,
        missing_keywords: Optional[List[str]] = None,
    ) -> None:
        """Update candidate answer after evaluation."""
        query = """
            UPDATE candidate_answers
            SET
                score = ?,
                feedback = ?,
                matched_keywords_json = ?,
                missing_keywords_json = ?,
                evaluated_at = ?
            WHERE answer_id = ?
        """
        self.execute_query(
            query,
            (
                score,
                feedback,
                to_json(matched_keywords or []),
                to_json(missing_keywords or []),
                current_timestamp(),
                answer_id,
            ),
        )

        self.insert_audit_log(
            event_type="candidate_answer_evaluated",
            event_description="Candidate answer evaluated",
            entity_type="candidate_answers",
            entity_id=answer_id,
            metadata={"score": score},
        )

    # ---------------------------------------------------------------------
    # Fetch methods
    # ---------------------------------------------------------------------

    def get_job_description(self, jd_id: int) -> Optional[Dict[str, Any]]:
        """Fetch job description by id."""
        return self.fetch_one(
            "SELECT * FROM job_descriptions WHERE jd_id = ?",
            (jd_id,),
        )

    def get_latest_job_description(self) -> Optional[Dict[str, Any]]:
        """Fetch latest job description."""
        return self.fetch_one(
            "SELECT * FROM job_descriptions ORDER BY jd_id DESC LIMIT 1"
        )

    def get_candidate(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        """Fetch candidate by id."""
        return self.fetch_one(
            "SELECT * FROM candidates WHERE candidate_id = ?",
            (candidate_id,),
        )

    def get_latest_candidate(self) -> Optional[Dict[str, Any]]:
        """Fetch latest candidate."""
        return self.fetch_one(
            "SELECT * FROM candidates ORDER BY candidate_id DESC LIMIT 1"
        )

    def get_questions_by_jd(self, jd_id: int) -> List[Dict[str, Any]]:
        """Fetch all questions for a JD."""
        return self.fetch_all(
            """
            SELECT *
            FROM interview_questions
            WHERE jd_id = ?
            ORDER BY question_order ASC, question_id ASC
            """,
            (jd_id,),
        )

    def get_answers_by_candidate(self, candidate_id: int) -> List[Dict[str, Any]]:
        """Fetch all answers submitted by candidate."""
        return self.fetch_all(
            """
            SELECT
                ca.*,
                iq.question_text,
                iq.skill,
                iq.question_type,
                iq.expected_keywords_json,
                iq.max_score
            FROM candidate_answers ca
            JOIN interview_questions iq
                ON ca.question_id = iq.question_id
            WHERE ca.candidate_id = ?
            ORDER BY ca.answer_id ASC
            """,
            (candidate_id,),
        )

    def get_latest_report_by_candidate(
        self,
        candidate_id: int,
    ) -> Optional[Dict[str, Any]]:
        """Fetch latest report for candidate."""
        return self.fetch_one(
            """
            SELECT *
            FROM evaluation_reports
            WHERE candidate_id = ?
            ORDER BY report_id DESC
            LIMIT 1
            """,
            (candidate_id,),
        )

    def get_audit_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch latest audit logs."""
        return self.fetch_all(
            """
            SELECT *
            FROM audit_logs
            ORDER BY audit_id DESC
            LIMIT ?
            """,
            (limit,),
        )

    def get_model_execution_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch latest model execution logs."""
        return self.fetch_all(
            """
            SELECT *
            FROM model_execution_logs
            ORDER BY log_id DESC
            LIMIT ?
            """,
            (limit,),
        )

    def get_table_counts(self) -> Dict[str, int]:
        """Return count of rows in each core table."""
        tables = [
            "job_descriptions",
            "candidates",
            "interview_questions",
            "candidate_answers",
            "evaluation_reports",
            "audit_logs",
            "model_execution_logs",
        ]

        counts = {}
        with self.connect() as conn:
            cursor = conn.cursor()
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) AS count FROM {table}")
                counts[table] = cursor.fetchone()["count"]

        return counts

    def get_latest_records_summary(self) -> Dict[str, Any]:
        """Return latest records for Logs/Settings inspection."""
        return {
            "latest_job_description": self.get_latest_job_description(),
            "latest_candidate": self.get_latest_candidate(),
            "latest_audit_logs": self.get_audit_logs(limit=10),
            "latest_model_execution_logs": self.get_model_execution_logs(limit=10),
            "table_counts": self.get_table_counts(),
        }


def run_database_smoke_test() -> None:
    """
    Run a simple database smoke test.

    This is useful in Jupyter/cloud terminal where Streamlit UI may not be used.
    """
    db = DatabaseManager()
    db.initialize_database()

    print("Database initialized successfully.")
    print("Tables created successfully.")
    print("Current table counts:")
    print(db.get_table_counts())


if __name__ == "__main__":
    run_database_smoke_test()