"""Practice page — answer questions one by one."""
import streamlit as st

from services.api import generate_questions
from services.n8n_client import N8NError
from services.state import (
    init_state, start_session, save_answer, skip_question, go_to_question,
    completion_stats, lock_session, get_extraction_by_id,
    SESSION, CURRENT_EXTRACTION_ID, log_debug, PREFERENCES,
)
from components.ui import page_setup, hero, empty_state, pill
from components.question_card import render_question_card


page_setup(title="Practice", icon="🎤")


# ====================================================
#  PHASE 1: kick off question generation if needed
# ====================================================
pending_count = st.session_state.pop("pending_question_count", None)
pending_eid = st.session_state.pop("pending_extraction_id", None)

if pending_count and pending_eid:
    extraction = get_extraction_by_id(pending_eid)
    if not extraction:
        st.error("Could not find that extraction. Go back to Extract page.")
        st.stop()

    with st.spinner(f"Generating {pending_count} questions… (10-20 sec)"):
        try:
            questions = generate_questions(
                jd_data=extraction["data"],
                difficulty=extraction["input"].get("difficulty", "medium"),
                count=pending_count,
            )
        except N8NError as e:
            st.error(f"⚠️ {e}")
            st.stop()

    log_debug("generate /questions", questions)

    if not questions:
        st.error("Failed to generate questions. Check your /questions webhook in n8n.")
        st.stop()

    start_session(pending_eid, questions)


# ====================================================
#  PHASE 2: practice UI
# ====================================================
session = st.session_state.get(SESSION)

if not session:
    hero(title="🎤 Practice", subtitle="No active session.")
    empty_state(
        icon="🎯",
        message="Start a practice session from the Extract page.",
        cta="Extract a Job Description → click 'Generate questions & start practice' at the bottom.",
    )
    st.stop()

questions = session["questions"]
idx = session["current_index"]
total = len(questions)
q = questions[idx]
locked = session.get("submitted", False)

# Header
stats = completion_stats()
extraction = get_extraction_by_id(st.session_state.get(CURRENT_EXTRACTION_ID))
role_title = (extraction or {}).get("data", {}).get("role", {}).get("title") or "Practice session"

st.markdown(
    f"""
    <div class="hero">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
                <h1 style="margin:0;font-size:1.5rem">🎤 {role_title}</h1>
                <p style="margin:0.25rem 0 0 0">
                    {pill("Locked" if locked else "In progress",
                          variant="rose" if locked else "default")}
                </p>
            </div>
            <div style="text-align:right">
                <div style="font-size:2rem;font-weight:600">{stats['pct']}%</div>
                <div style="font-size:0.8rem;color:#9CA3AF">
                    {stats['answered']} answered · {stats['skipped']} skipped · {stats['total']} total
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.progress(stats["pct"] / 100)

# Question card
render_question_card(q, idx, total)

# Navigation
st.markdown("---")
cols = st.columns([1, 1, 1, 1, 2])

with cols[0]:
    if st.button("← Previous", use_container_width=True, disabled=idx == 0):
        go_to_question(idx - 1)
        st.rerun()

with cols[1]:
    if st.button("⏭️ Skip", use_container_width=True, disabled=locked):
        skip_question(q["id"])
        if idx < total - 1:
            go_to_question(idx + 1)
        st.rerun()

with cols[2]:
    is_last = idx == total - 1
    next_label = "Last" if is_last else "Next →"
    if st.button(next_label, use_container_width=True, disabled=is_last):
        go_to_question(idx + 1)
        st.rerun()

with cols[4]:
    all_done = (stats["answered"] + stats["skipped"]) >= stats["total"]
    if not locked:
        if st.button(
            "🏁 Submit all & evaluate",
            type="primary",
            use_container_width=True,
            disabled=not all_done,
            help=None if all_done else "Answer or skip every question first.",
        ):
            lock_session()
            st.switch_page("pages/results.py")
    else:
        if st.button("🏆 Go to results", type="primary", use_container_width=True):
            st.switch_page("pages/results.py")

# Navigator
with st.expander("Jump to question"):
    grid = st.columns(5)
    for i, qn in enumerate(questions):
        ans = session["answers"].get(qn["id"], {})
        prefix = "✅" if ans.get("content") else ("⏭️" if ans.get("mode") == "skipped" else "⭕")
        is_current = i == idx
        with grid[i % 5]:
            if st.button(
                f"{prefix} Q{i+1}{' •' if is_current else ''}",
                key=f"jump_{i}",
                use_container_width=True,
            ):
                go_to_question(i)
                st.rerun()
