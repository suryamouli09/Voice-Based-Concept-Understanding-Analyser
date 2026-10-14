import streamlit as st
from pathlib import Path
from utils.session import initialize_session

# -----------------------------------------------------------------------------
# Global Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="VBCUA | Voice Concept Intelligence",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Inject Modern CSS Stylesheet
# -----------------------------------------------------------------------------
css_file = Path("styles/style.css")
if css_file.exists():
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize Session State
initialize_session()

# -----------------------------------------------------------------------------
# Modern Streamlit Navigation Hierarchy
# -----------------------------------------------------------------------------
evaluator_page = st.Page(
    "views/evaluator.py",
    title="Voice Evaluator",
    icon="🎙️",
    default=True
)

dashboard_page = st.Page(
    "views/dashboard.py",
    title="Analytics Dashboard",
    icon="📊"
)

history_page = st.Page(
    "views/history.py",
    title="Assessment History",
    icon="📜"
)

concepts_page = st.Page(
    "views/concepts.py",
    title="Concept Knowledge Base",
    icon="📚"
)

about_page = st.Page(
    "views/about.py",
    title="Architecture & Specs",
    icon="ℹ️"
)

# Grouped Navigation
pg = st.navigation({
    "Workspace": [evaluator_page, dashboard_page, history_page],
    "Reference & Documentation": [concepts_page, about_page]
})

# Sidebar branding & system health
with st.sidebar:
    st.markdown("## 🎙️ **VBCUA**")
    st.caption("Speech Intelligence & Concept Evaluator")
    st.markdown("---")

pg.run()