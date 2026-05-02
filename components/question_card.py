"""Question card + answer area used in the Practice page."""
import streamlit as st

from components.ui import pill
from services.state import save_answer, SESSION


def render_question_card(question: dict, index: int, total: int) -> None:
    """Render a single question with answer textarea (auto-saves on edit)."""
    sess = st.session_state[SESSION]
    locked = sess.get("submitted", False) if sess else True

    q_id = question.get("id", f"q{index+1}")
    existing = sess["answers"].get(q_id, {}).get("content", "") if sess else ""

    # Header
    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:flex-end;
                    margin-bottom:0.5rem">
            <div style="font-size:0.85rem;color:#9CA3AF">
                Question {index + 1} of {total}
            </div>
            <div>
                {pill(question.get("category", "general").replace("_", " ").title())}
                {pill(question.get("expected_depth", "moderate"), variant="amber")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Question text
    st.markdown(f"### {question.get('question', '—')}")
    if question.get("focus_area"):
        st.caption(f"🎯 Focus: {question['focus_area']}")

    # Answer field
    answer = st.text_area(
        "Your answer",
        value=existing,
        height=200,
        key=f"answer_{q_id}",
        placeholder="Take your time. Structure your thoughts before writing.",
        disabled=locked,
        label_visibility="collapsed",
    )

    # Auto-save on every keystroke (only if not locked)
    if not locked and answer != existing:
        save_answer(q_id, answer)


def render_question_review(question: dict, answer_content: str, mode: str,
                            index: int, feedback: dict | None = None) -> None:
    """Read-only question view used after submission / on results page."""
    q_id = question.get("id", f"q{index+1}")

    label_extra = ""
    if feedback:
        score = feedback.get("score", 0)
        label_extra = f" · **{score}/10**"

    title = question.get("question", "—")
    truncated = title[:80] + ("…" if len(title) > 80 else "")

    with st.expander(f"Q{index + 1} · {truncated}{label_extra}"):
        st.markdown(f"**Question:** {title}")
        st.caption(
            f"Category: {question.get('category', 'N/A')}  ·  "
            f"Focus: {question.get('focus_area', 'N/A')}  ·  "
            f"Depth: {question.get('expected_depth', 'N/A')}"
        )

        st.markdown("**Your answer:**")
        if mode == "skipped":
            st.caption("⏭️ Skipped")
        elif answer_content:
            st.write(answer_content)
        else:
            st.caption("— no answer —")

        if feedback:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Strengths**")
                for s in feedback.get("strengths", []):
                    st.markdown(f"- {s}")
            with col2:
                st.markdown("**⚠️ Gaps**")
                for g in feedback.get("gaps", []):
                    st.markdown(f"- {g}")

            if feedback.get("feedback"):
                st.info(feedback["feedback"])

            if feedback.get("model_answer"):
                with st.expander("👀 Model answer"):
                    st.write(feedback["model_answer"])
        else:
            ideal = question.get("ideal_answer_points", [])
            if ideal:
                with st.expander("Ideal answer points"):
                    for p in ideal:
                        st.markdown(f"- {p}")
