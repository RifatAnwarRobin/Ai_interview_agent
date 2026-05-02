"""Centralized session state. All keys and helpers live here.

Replace this file with a DB-backed version later — call sites won't change.
"""
from datetime import datetime
import streamlit as st


# ===== Session keys (constants) =====
USER_NAME = "user_name"
EXTRACTIONS = "extractions"
LAST_EXTRACTION_ID = "last_extraction_id"
CURRENT_EXTRACTION_ID = "current_extraction_id"
SESSION = "session"          # active practice session
EVALUATION = "evaluation"    # results from /evaluate
PREFERENCES = "preferences"
DEBUG = "debug_messages"     # list for capturing raw responses


def init_state() -> None:
    """Idempotent. Call at the top of every page."""
    defaults = {
        USER_NAME: "Guest",
        EXTRACTIONS: [],
        LAST_EXTRACTION_ID: None,
        CURRENT_EXTRACTION_ID: None,
        SESSION: None,
        EVALUATION: None,
        DEBUG: [],
        PREFERENCES: {
            "default_difficulty": "medium",
            "default_question_count": 10,
            "show_debug": False,
        },
    }
    for key, val in defaults.items():
        st.session_state.setdefault(key, val)


# ===== Extractions =====

def save_extraction(user_input: dict, data: dict) -> str:
    """Store a new extraction; return its id."""
    eid = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state[EXTRACTIONS].append({
        "id": eid,
        "created_at": datetime.now().isoformat(),
        "input": user_input,
        "data": data,
    })
    st.session_state[LAST_EXTRACTION_ID] = eid
    st.session_state[CURRENT_EXTRACTION_ID] = eid
    return eid


def get_last_extraction() -> dict | None:
    return st.session_state[EXTRACTIONS][-1] if st.session_state[EXTRACTIONS] else None


def get_extraction_by_id(eid: str | None) -> dict | None:
    if not eid:
        return None
    return next((e for e in st.session_state[EXTRACTIONS] if e["id"] == eid), None)


def delete_extraction(eid: str) -> None:
    st.session_state[EXTRACTIONS] = [
        e for e in st.session_state[EXTRACTIONS] if e["id"] != eid
    ]


def clear_history() -> None:
    st.session_state[EXTRACTIONS] = []
    st.session_state[LAST_EXTRACTION_ID] = None


# ===== Practice session =====

def start_session(extraction_id: str, questions: list) -> None:
    """Begin a fresh practice session."""
    st.session_state[CURRENT_EXTRACTION_ID] = extraction_id
    st.session_state[SESSION] = {
        "questions": questions,
        "current_index": 0,
        "answers": {},
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "submitted": False,
    }
    st.session_state[EVALUATION] = None


def save_answer(question_id: str, content: str) -> None:
    sess = st.session_state[SESSION]
    if sess and not sess["submitted"]:
        sess["answers"][question_id] = {
            "mode": "text",
            "content": content.strip(),
        }


def skip_question(question_id: str) -> None:
    sess = st.session_state[SESSION]
    if sess and not sess["submitted"]:
        sess["answers"][question_id] = {"mode": "skipped", "content": ""}


def go_to_question(index: int) -> None:
    sess = st.session_state[SESSION]
    if sess and 0 <= index < len(sess["questions"]):
        sess["current_index"] = index


def lock_session() -> None:
    """Mark answers as submitted (locks editing)."""
    sess = st.session_state[SESSION]
    if sess:
        sess["submitted"] = True
        sess["completed_at"] = datetime.now().isoformat()


def reset_session() -> None:
    st.session_state[SESSION] = None
    st.session_state[EVALUATION] = None


def get_qa_pairs() -> list[dict]:
    """Build the payload list to send to /evaluate."""
    sess = st.session_state[SESSION]
    if not sess:
        return []
    return [
        {
            "question_id": q["id"],
            "question": q["question"],
            "category": q.get("category"),
            "focus_area": q.get("focus_area"),
            "expected_depth": q.get("expected_depth"),
            "ideal_answer_points": q.get("ideal_answer_points", []),
            "answer": sess["answers"].get(q["id"], {}).get("content", ""),
            "skipped": sess["answers"].get(q["id"], {}).get("mode") == "skipped",
        }
        for q in sess["questions"]
    ]


def completion_stats() -> dict:
    sess = st.session_state[SESSION]
    if not sess:
        return {"answered": 0, "skipped": 0, "total": 0, "pct": 0}
    total = len(sess["questions"])
    answered = sum(1 for a in sess["answers"].values() if a.get("content"))
    skipped = sum(1 for a in sess["answers"].values() if a.get("mode") == "skipped")
    return {
        "answered": answered,
        "skipped": skipped,
        "total": total,
        "pct": int(100 * (answered + skipped) / total) if total else 0,
    }


# ===== Debug capture =====

def log_debug(label: str, payload) -> None:
    """Capture raw payloads when debug mode is on."""
    if st.session_state[PREFERENCES].get("show_debug"):
        st.session_state[DEBUG].append({
            "ts": datetime.now().isoformat(timespec="seconds"),
            "label": label,
            "payload": payload,
        })


def clear_debug() -> None:
    st.session_state[DEBUG] = []
