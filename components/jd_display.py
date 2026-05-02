"""Render an extracted Job Description in a polished layout."""
import json
import streamlit as st

from components.ui import section, pills


def _safe_get(d: dict, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur if cur is not None else default


def _as_text(value, default: str = "—") -> str:
    """Coerce any LLM value (str / list / dict / None) to a display string.

    The LLM sometimes returns a list (e.g. multiple office locations) where
    we expect a string. st.metric() only accepts str/int/float, so we flatten.
    """
    if value is None or value == "":
        return default
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        flat = [_as_text(v, "") for v in value if v not in (None, "")]
        return ", ".join(s for s in flat if s) or default
    if isinstance(value, dict):
        flat = [f"{k}: {_as_text(v, '')}" for k, v in value.items() if v]
        return " · ".join(s for s in flat if s) or default
    return str(value)


def render_extraction(data: dict) -> None:
    """Display a fully-extracted Job Description."""
    if not data:
        st.warning("No data to display.")
        return

    # Top metrics — all values coerced to strings since LLMs sometimes
    # return lists/dicts where we expect a single label.
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Role", _as_text(_safe_get(data, "role", "title")))
    c2.metric("Seniority", _as_text(_safe_get(data, "role", "seniority_level")))
    c3.metric("Location", _as_text(_safe_get(data, "role", "location")))
    c4.metric("Difficulty", _as_text(data.get("difficulty_level")))

    # Summary
    summary = data.get("candidate_summary")
    if summary:
        st.info(summary)

    left, right = st.columns(2, gap="large")

    with left:
        section("Role details", "🎯")
        role = data.get("role", {})
        _kv_block({
            "Employment type": role.get("employment_type"),
            "Remote policy": role.get("remote_policy"),
            "Department": role.get("department"),
        })
        salary = role.get("salary_range", {}) or {}
        if any(salary.values()):
            st.caption(
                f"💰 {salary.get('min') or '—'} – {salary.get('max') or '—'} "
                f"{salary.get('currency') or ''} / {salary.get('period') or ''}"
            )

        section("Company", "🏢")
        company = data.get("company", {})
        _kv_block({
            "Name": company.get("name"),
            "Industry": company.get("industry"),
            "Size": company.get("size"),
        })
        if company.get("about"):
            st.caption(company["about"])

        section("Requirements", "📋")
        needs = data.get("what_they_need", {})
        exp_min = needs.get("experience_years_min")
        exp_max = needs.get("experience_years_max")
        if exp_min or exp_max:
            st.caption(f"⏱️ Experience: {exp_min or 0} – {exp_max or '∞'} years")

        edu = needs.get("education", {}) or {}
        if edu.get("degree_required"):
            fields = edu.get("fields") or []
            st.caption(
                f"🎓 {edu['degree_required']} · {', '.join(fields) if fields else 'Any'}"
            )

        st.markdown("**Must-have skills**")
        pills(needs.get("must_have_skills", []), variant="rose")

        st.markdown("**Nice to have**")
        pills(needs.get("nice_to_have_skills", []), variant="green")

    with right:
        section("Tools & tech", "🛠️")
        pills(data.get("tools_and_technologies", []))

        section("Soft skills", "🤝")
        pills(data.get("soft_skills", []), variant="amber")

        section("Resume keywords", "🔑")
        st.caption("Include in your CV for ATS screening")
        pills(data.get("keywords_for_resume", []), variant="gray")

        section("Benefits", "🎁")
        benefits = data.get("benefits_and_perks", [])
        if benefits:
            for b in benefits:
                st.markdown(f"- {b}")
        else:
            st.caption("— not listed —")

    section("What you'll do", "💼")
    duties = data.get("what_you_will_do", [])
    if duties:
        for d in duties:
            st.markdown(f"- {d}")
    else:
        st.caption("— not listed —")

    st.markdown("---")
    col1, _ = st.columns([1, 3])
    with col1:
        st.download_button(
            "⬇️ Download JSON",
            json.dumps(data, indent=2),
            file_name="extracted_jd.json",
            mime="application/json",
            use_container_width=True,
        )


def _kv_block(pairs: dict) -> None:
    rows = [(k, _as_text(v, "")) for k, v in pairs.items()]
    rows = [(k, v) for k, v in rows if v]
    if not rows:
        st.caption("— no details —")
        return
    for k, v in rows:
        st.markdown(
            f'<div style="display:flex;gap:0.5rem;padding:0.25rem 0;'
            f'border-bottom:1px solid rgba(255,255,255,0.04)">'
            f'<span style="color:#9CA3AF;min-width:120px;font-size:0.88rem">{k}</span>'
            f'<span style="color:#E6E7EA;font-size:0.88rem">{v}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )