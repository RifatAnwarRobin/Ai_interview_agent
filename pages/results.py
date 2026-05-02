"""Results page — evaluation feedback per question + overall summary."""
import json
import streamlit as st

from services.api import evaluate_answers
from services.n8n_client import N8NError
from services.state import (
    init_state, get_qa_pairs, get_extraction_by_id, reset_session, log_debug,
    SESSION, EVALUATION, CURRENT_EXTRACTION_ID,
)
from components.ui import page_setup, hero, empty_state, pill
from components.question_card import render_question_review


page_setup(title="Results", icon="🏆")

session = st.session_state.get(SESSION)
if not session:
    hero(title="🏆 Results", subtitle="No session to evaluate.")
    empty_state(icon="🎯", message="Complete a practice session first.")
    st.stop()

# ===== Trigger evaluation if not done =====
if st.session_state.get(EVALUATION) is None:
    extraction = get_extraction_by_id(st.session_state.get(CURRENT_EXTRACTION_ID))
    jd_data = extraction["data"] if extraction else {}

    with st.spinner("Evaluating your answers… this may take 30-60 seconds"):
        try:
            result = evaluate_answers(jd_data=jd_data, qa_pairs=get_qa_pairs())
        except N8NError as e:
            st.error(f"⚠️ {e}")
            st.stop()

    log_debug("evaluate /evaluate", result)

    if not result:
        st.error("Evaluation failed to parse. Check your /evaluate webhook in n8n.")
        st.stop()

    st.session_state[EVALUATION] = result

evaluation = st.session_state[EVALUATION]
overall = evaluation.get("overall", {}) if isinstance(evaluation, dict) else {}

# ===== Hero =====
rating_colors = {
    "weak": "rose", "developing": "amber", "solid": "default",
    "strong": "green", "excellent": "green",
}
rating = (overall.get("rating") or "—").lower()
score = overall.get("score", 0)

st.markdown(
    f"""
    <div class="hero">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
                <h1 style="margin:0">🏆 Your results</h1>
                <p style="margin:0.5rem 0 0 0">
                    {pill(rating.title(), variant=rating_colors.get(rating, "default"))}
                </p>
            </div>
            <div style="text-align:right">
                <div style="font-size:3rem;font-weight:700;line-height:1">
                    {score}<span style="font-size:1.5rem;color:#9CA3AF">/10</span>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ===== Strengths & weaknesses =====
col_l, col_r = st.columns(2, gap="large")
with col_l:
    st.markdown("### ✅ Strengths")
    strengths = overall.get("strengths", []) or []
    if strengths:
        for s in strengths:
            st.markdown(f"- {s}")
    else:
        st.caption("— not specified —")

with col_r:
    st.markdown("### 📈 Areas to improve")
    weaknesses = overall.get("weaknesses", []) or []
    if weaknesses:
        for w in weaknesses:
            st.markdown(f"- {w}")
    else:
        st.caption("— not specified —")

if overall.get("recommendation"):
    st.markdown("### 💡 Recommendation")
    st.info(overall["recommendation"])

next_steps = overall.get("next_steps", []) or []
if next_steps:
    st.markdown("### 🎯 Next steps")
    for step in next_steps:
        st.markdown(f"- {step}")

st.markdown("---")

# ===== Per-question review =====
st.markdown("### 📋 Question-by-question review")

per_q_list = evaluation.get("per_question", []) if isinstance(evaluation, dict) else []
per_q_map = {item.get("question_id"): item for item in per_q_list if isinstance(item, dict)}

for i, q in enumerate(session["questions"]):
    ans = session["answers"].get(q["id"], {})
    feedback = per_q_map.get(q["id"])
    render_question_review(
        question=q,
        answer_content=ans.get("content", ""),
        mode=ans.get("mode", "none"),
        index=i,
        feedback=feedback,
    )

# ===== Export & restart =====
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    full_report = {
        "extraction_id": st.session_state.get(CURRENT_EXTRACTION_ID),
        "questions": session["questions"],
        "answers": session["answers"],
        "evaluation": evaluation,
    }
    st.download_button(
        "⬇️ Download full report (JSON)",
        json.dumps(full_report, indent=2),
        file_name="interview_report.json",
        use_container_width=True,
    )
with col2:
    if st.button("🔄 Start new practice", use_container_width=True):
        reset_session()
        st.switch_page("pages/extract.py")
