"""Extract Job Description page."""
import streamlit as st

from services.api import extract_jd
from services.n8n_client import N8NError
from services.parser import get_debug_info
from services.state import save_extraction, get_last_extraction, log_debug, PREFERENCES
from components.ui import page_setup, hero
from components.jd_display import render_extraction


page_setup(title="Extract from Job Description", icon="📝")

hero(
    title="📝 Extract job description",
    subtitle="Paste any Job Description from LinkedIn, Indeed, or a company site. "
             "We'll extract everything that matters.",
)

# ===== Form =====
col_main, col_opts = st.columns([2, 1], gap="large")

with col_main:
    input_type = st.selectbox(
        "What are you preparing for?",
        ["Job Interview", "Understanding check"],
        index=0,
    )
    if input_type == "Job Interview":
        jd_text = st.text_area(
            "Paste job description",
            height=280,
            placeholder="Paste the full Job Description here — we handle messy formatting automatically.",
        )
    else:
        jd_text = st.text_input("Topic", value="Python")

with col_opts:
    difficulty = st.selectbox(
        "Difficulty level",
        ["easy", "medium", "hard", "expert"],
        index=["easy", "medium", "hard", "expert"].index(
            st.session_state[PREFERENCES]["default_difficulty"]
        ),
    )
    show_debug = st.toggle(
        "Debug mode",
        value=st.session_state[PREFERENCES].get("show_debug", False),
        help="Show raw n8n responses inline.",
    )
    st.session_state[PREFERENCES]["show_debug"] = show_debug

    st.markdown("<div style='padding-top:1.25rem'></div>", unsafe_allow_html=True)
    submit = st.button(
        "✨ Extract now",
        type="primary",
        use_container_width=True,
        disabled=not (jd_text or "").strip(),
    )


# ===== Submit handler =====
if submit:
    user_input = {
        "input_type": input_type,
        "difficulty": difficulty,
        "jd_text": jd_text.strip(),
    }

    with st.spinner("Analyzing… this usually takes 10-20 seconds"):
        try:
            data = extract_jd(
                jd_text=jd_text,
                difficulty=difficulty,
                input_type=input_type,
            )
        except N8NError as e:
            st.error(f"⚠️ {e}")
            st.stop()

    log_debug("extract /gather", data)

    if data is None:
        st.error("Could not parse LLM output as JSON.")
        st.info(
            "Common fixes: (1) check your LLM system prompt tells it to return JSON only, "
            "(2) make sure Respond to Webhook is the last node in the chain."
        )
        st.stop()

    eid = save_extraction(user_input, data)
    st.success(f"✅ Extracted successfully — saved as #{eid}")


# ===== Latest result =====
last = get_last_extraction()
if last:
    if show_debug:
        with st.expander("🔍 Debug — last response"):
            for entry in st.session_state.get("debug_messages", [])[-3:]:
                st.caption(f"{entry['ts']} · {entry['label']}")
                st.json(entry["payload"])
                st.caption(f"Shape: {get_debug_info(entry['payload'])}")
                st.markdown("---")

    st.markdown("---")
    st.markdown(
        f"#### Results for: `{last['data'].get('role', {}).get('title') or 'Untitled'}`"
    )
    render_extraction(last["data"])

    # Hand-off to practice
    st.markdown("---")
    col_a, col_b, col_c = st.columns([2, 1, 2])
    with col_b:
        question_count = st.selectbox(
            "Questions per session",
            [5, 10, 15],
            index=[5, 10, 15].index(
                st.session_state[PREFERENCES].get("default_question_count", 10)
            ),
            key="question_count_select",
        )

    if st.button("Generate questions & start practice",
                 type="primary", use_container_width=True):
        st.session_state["pending_question_count"] = question_count
        st.session_state["pending_extraction_id"] = last["id"]
        st.switch_page("pages/practice.py")
