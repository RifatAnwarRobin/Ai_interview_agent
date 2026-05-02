"""Interview Copilot — entry point.

Run with:
    streamlit run app.py
"""
import streamlit as st

from components.ui import page_setup, hero, empty_state


page_setup(title="Home", icon="🎯")

hero(
    title=f"Welcome back, {st.session_state['user_name']} 👋",
    subtitle="Paste a job description, generate tailored interview questions, "
             "and track your progress over time.",
)

# Quick stats
extractions = st.session_state.get("extractions", [])
sessions_completed = sum(
    1 for _ in extractions  # placeholder; later track real practice runs
)

c1, c2, c3 = st.columns(3)
c1.metric("Extractions", len(extractions))
c2.metric("Practice sessions", sessions_completed)
c3.metric("Saved", len(extractions))

st.markdown("---")

# How it works
st.markdown("### How it works")
cols = st.columns(3)
for col, (step, title, desc) in zip(cols, [
    ("Step 1", "Extract a Job Description",
     "Paste a job description to see role details, skills, and ATS keywords."),
    ("Step 2", "Practice questions",
     "Generate tailored interview questions and answer them at your own pace."),
    ("Step 3", "Get feedback",
     "Submit your answers for an evaluation with strengths, gaps, and next steps."),
]):
    with col:
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">{step}</div>
                <div class="card-value" style="font-size:1.1rem">{title}</div>
                <p style="color:#9CA3AF;font-size:0.88rem;margin-top:0.5rem">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")
st.markdown("### Recent activity")

recent = extractions[-3:]
if not recent:
    empty_state(
        icon="📭",
        message="No extractions yet.",
        cta="Open the Extract page from the sidebar to get started.",
    )
else:
    for item in reversed(recent):
        role = item["data"].get("role", {}).get("title") or "Untitled"
        st.markdown(
            f"""
            <div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <div style="font-weight:500">{role}</div>
                        <div style="color:#9CA3AF;font-size:0.8rem">
                            {item['created_at'][:16].replace('T', ' · ')}
                        </div>
                    </div>
                    <div style="color:#6B7280;font-size:0.75rem">#{item['id']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
