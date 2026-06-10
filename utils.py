"""
Common utility functions for AI Interview Evaluation System.

Module 1: Basic helper placeholders.
"""

from datetime import datetime
import json


def current_timestamp() -> str:
    """Return current timestamp as ISO-like string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def to_json(data) -> str:
    """Safely convert Python object to JSON string."""
    return json.dumps(data, ensure_ascii=False, default=str)


def from_json(data: str, default=None):
    """Safely parse JSON string."""
    if default is None:
        default = {}
    try:
        return json.loads(data) if data else default
    except Exception:
        return default


def clean_text(text: str) -> str:
    """Basic text cleanup."""
    if not text:
        return ""
    return " ".join(str(text).strip().split())
