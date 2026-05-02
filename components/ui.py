"""Reusable UI building blocks. Import in every page."""
from pathlib import Path
import streamlit as st


_ROOT = Path(__file__).resolve().parent.parent


def load_css() -> None:
    """Inject custom stylesheet. Call once per page."""
    css_path = _ROOT / "assets" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def hero(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pill(text: str, variant: str = "default") -> str:
    cls = "pill" if variant == "default" else f"pill pill-{variant}"
    return f'<span class="{cls}">{text}</span>'


def pills(items: list, variant: str = "default") -> None:
    if not items:
        st.markdown(
            '<span style="color:#6B7280;font-size:0.9rem">— none listed —</span>',
            unsafe_allow_html=True,
        )
        return
    html = " ".join(pill(str(i), variant) for i in items)
    st.markdown(html, unsafe_allow_html=True)


def section(title: str, icon: str = "") -> None:
    prefix = f"{icon} " if icon else ""
    st.markdown(f"### {prefix}{title}")


def empty_state(icon: str, message: str, cta: str = "") -> None:
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-state-icon">{icon}</div>
            <p>{message}</p>
            {f'<p style="margin-top:1rem">{cta}</p>' if cta else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_dot(color: str, label: str) -> str:
    return f'<span class="status-dot {color}"></span>{label}'


def render_sidebar_branding() -> None:
    """Consistent sidebar header."""
    from services.config import config

    user = st.session_state.get("user_name", "Guest")
    st.sidebar.markdown(
        f"""
        <div style="padding:0.5rem 0 1.5rem 0;border-bottom:1px solid rgba(255,255,255,0.06);
                    margin-bottom:1rem">
            <div style="font-size:1.25rem;font-weight:600;letter-spacing:-0.01em">
                🎯 {config.APP_NAME}
            </div>
            <div style="font-size:0.78rem;color:#9CA3AF;margin-top:0.15rem">
                {config.APP_TAGLINE}
            </div>
        </div>
        <div style="padding:0.75rem 1rem;background:rgba(99,102,241,0.08);
                    border:1px solid rgba(99,102,241,0.2);border-radius:8px;
                    margin-bottom:1.5rem">
            <div style="font-size:0.7rem;color:#9CA3AF;text-transform:uppercase;
                        letter-spacing:0.05em">Signed in as</div>
            <div style="font-weight:500;margin-top:0.15rem">{user}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_setup(title: str, icon: str = "🎯") -> None:
    """Boilerplate that every page calls first.

    Sets page config + loads CSS + initializes state + renders sidebar branding.
    """
    from services.state import init_state
    from services.config import config

    st.set_page_config(
        page_title=f"{title} · {config.APP_NAME}",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_css()
    init_state()
    render_sidebar_branding()
