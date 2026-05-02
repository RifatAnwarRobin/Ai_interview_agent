"""Dashboard page - overview of activity and aggregated insights."""
from collections import Counter
import streamlit as st

from services.state import EXTRACTIONS
from components.ui import page_setup, hero, empty_state, pills


page_setup(title="Dashboard", icon="📊")

hero(
    title="📊 Dashboard",
    subtitle="Skills you've seen, tools that keep coming up, and roles you're tracking.",
)

extractions = st.session_state[EXTRACTIONS]

if not extractions:
    empty_state(
        icon="📊",
        message="Nothing to show yet — extract a JD first.",
        cta="Open the Extract page from the sidebar.",
    )
    st.stop()


# Metrics
total = len(extractions)
unique_roles = len({
    e["data"].get("role", {}).get("title")
    for e in extractions
    if e["data"].get("role", {}).get("title")
})
unique_companies = len({
    e["data"].get("company", {}).get("name")
    for e in extractions
    if e["data"].get("company", {}).get("name")
})

c1, c2, c3 = st.columns(3)
c1.metric("Total extractions", total)
c2.metric("Unique roles", unique_roles)
c3.metric("Unique companies", unique_companies)

st.markdown("---")


def _aggregate(field_path: tuple) -> Counter:
    counter: Counter = Counter()
    for e in extractions:
        cur = e["data"]
        for key in field_path:
            cur = cur.get(key) if isinstance(cur, dict) else None
            if cur is None:
                break
        if isinstance(cur, list):
            counter.update(cur)
    return counter


tools = _aggregate(("tools_and_technologies",))
must = _aggregate(("what_they_need", "must_have_skills"))
soft = _aggregate(("soft_skills",))
keywords = _aggregate(("keywords_for_resume",))

col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.markdown("### 🛠️ Most common tools")
    if tools:
        pills([f"{n} ({c})" for n, c in tools.most_common(15)])
    else:
        st.caption("— no data yet —")

    st.markdown("### 🤝 Most common soft skills")
    if soft:
        pills([f"{n} ({c})" for n, c in soft.most_common(10)], variant="amber")
    else:
        st.caption("— no data yet —")

with col_r:
    st.markdown("### 🎯 Most required skills")
    if must:
        pills([f"{n} ({c})" for n, c in must.most_common(15)], variant="rose")
    else:
        st.caption("— no data yet —")

    st.markdown("### 🔑 Most common ATS keywords")
    if keywords:
        pills([f"{n} ({c})" for n, c in keywords.most_common(15)], variant="gray")
    else:
        st.caption("— no data yet —")

st.markdown("---")
st.markdown("### 🏷️ Difficulty distribution")
diff_counter = Counter(e["data"].get("difficulty_level") or "—" for e in extractions)
st.bar_chart(dict(diff_counter))
