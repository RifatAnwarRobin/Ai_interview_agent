"""History page — browse past extractions."""
import streamlit as st

from services.state import EXTRACTIONS, delete_extraction, clear_history
from components.ui import page_setup, hero, empty_state
from components.jd_display import render_extraction


page_setup(title="History", icon="📚")

hero(
    title="📚 Extraction history",
    subtitle="Every Job Description you've analyzed, searchable and exportable.",
)

extractions = st.session_state[EXTRACTIONS]

if not extractions:
    empty_state(
        icon="📭",
        message="No history yet.",
        cta="Extract your first Job Description to see it here.",
    )
    st.stop()

# Filters
col_search, col_filter, col_clear = st.columns([3, 1, 1])
with col_search:
    query = st.text_input(
        "🔍 Search by role or company",
        placeholder="e.g. 'Engineer' or 'Google'",
        label_visibility="collapsed",
    )
with col_filter:
    diff_filter = st.selectbox(
        "Difficulty",
        ["all", "entry", "mid", "senior", "lead", "executive",
         "easy", "medium", "hard", "expert"],
        label_visibility="collapsed",
    )
with col_clear:
    if st.button("🗑️ Clear all", use_container_width=True):
        clear_history()
        st.rerun()


def _matches(ext: dict) -> bool:
    role = (ext["data"].get("role", {}).get("title") or "").lower()
    company = (ext["data"].get("company", {}).get("name") or "").lower()
    diff = ext["data"].get("difficulty_level") or ""
    if query and query.lower() not in role and query.lower() not in company:
        return False
    if diff_filter != "all" and diff != diff_filter:
        return False
    return True


filtered = [e for e in reversed(extractions) if _matches(e)]

if not filtered:
    st.caption(f"No matches found (out of {len(extractions)} total).")
    st.stop()

st.caption(f"Showing {len(filtered)} of {len(extractions)} extractions")
st.markdown("---")

for ext in filtered:
    role = ext["data"].get("role", {}).get("title") or "Untitled"
    company = ext["data"].get("company", {}).get("name") or "Unknown"
    diff = ext["data"].get("difficulty_level") or "—"
    ts = ext["created_at"][:16].replace("T", " · ")

    with st.expander(f"🎯 **{role}** · {company} · `{diff}` · {ts}"):
        col_del, _ = st.columns([1, 5])
        with col_del:
            if st.button("🗑️ Delete", key=f"del_{ext['id']}"):
                delete_extraction(ext["id"])
                st.rerun()
        render_extraction(ext["data"])
