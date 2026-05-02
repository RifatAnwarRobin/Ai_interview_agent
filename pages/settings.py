"""Settings page — preferences and connection diagnostics."""
import streamlit as st

from services.config import config
from services.n8n_client import ping_webhook
from services.state import PREFERENCES, USER_NAME, clear_debug, DEBUG
from components.ui import page_setup, hero, status_dot


page_setup(title="Settings", icon="⚙️")

hero(
    title="⚙️ Settings",
    subtitle="Configure preferences and check your n8n connection.",
)

# ===== Profile =====
st.markdown("### 👤 Profile")
new_name = st.text_input("Display name", value=st.session_state[USER_NAME])
if new_name and new_name != st.session_state[USER_NAME]:
    st.session_state[USER_NAME] = new_name
    st.success("Name updated.")

st.markdown("---")

# ===== Preferences =====
st.markdown("### 🎛️ Preferences")
prefs = st.session_state[PREFERENCES]

col1, col2, col3 = st.columns(3)
with col1:
    prefs["default_difficulty"] = st.selectbox(
        "Default difficulty",
        ["easy", "medium", "hard", "expert"],
        index=["easy", "medium", "hard", "expert"].index(prefs["default_difficulty"]),
    )
with col2:
    prefs["default_question_count"] = st.selectbox(
        "Default question count",
        [5, 10, 15],
        index=[5, 10, 15].index(prefs.get("default_question_count", 10)),
    )
with col3:
    prefs["show_debug"] = st.toggle(
        "Always show debug info",
        value=prefs.get("show_debug", False),
    )

st.markdown("---")

# ===== n8n connection =====
st.markdown("### 🔌 n8n connection")

st.text_input(
    "Webhook base URL",
    value=config.WEBHOOK_BASE_URL,
    disabled=True,
    help="Set via N8N_WEBHOOK_URL environment variable.",
)

st.caption("Endpoints used by this app:")
st.markdown(
    f"""
    - `{config.WEBHOOK_BASE_URL}/gather` — JD extraction
    - `{config.WEBHOOK_BASE_URL}/questions` — Question generation
    - `{config.WEBHOOK_BASE_URL}/evaluate` — Answer evaluation
    """
)

if st.button("🔌 Test all three endpoints"):
    for endpoint in ("gather", "questions", "evaluate"):
        ok, msg = ping_webhook(endpoint)
        color = "green" if ok else "red"
        label = f"{endpoint}: {msg}"
        st.markdown(
            f'<div style="margin-top:0.5rem">{status_dot(color, label)}</div>',
            unsafe_allow_html=True,
        )

st.markdown("---")

# ===== Debug log =====
st.markdown("### 🪵 Debug log")
debug_log = st.session_state.get(DEBUG, [])
if not debug_log:
    st.caption("No debug entries yet (enable debug mode to capture responses).")
else:
    if st.button("Clear debug log"):
        clear_debug()
        st.rerun()
    for entry in reversed(debug_log[-10:]):
        with st.expander(f"{entry['ts']} · {entry['label']}"):
            st.json(entry["payload"])

st.markdown("---")

# ===== Danger zone =====
st.markdown("### 💥 Danger zone")
with st.expander("Reset all session data"):
    st.caption("Removes all extractions, sessions, and preferences. Cannot be undone.")
    if st.button("Reset everything", type="secondary"):
        st.session_state.clear()
        st.rerun()

st.markdown("---")
st.caption(f"{config.APP_NAME} · v{config.VERSION}")
