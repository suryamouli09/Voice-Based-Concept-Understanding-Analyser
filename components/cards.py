import streamlit as st

def feature_card(icon, title, description):
    """Reusable modern feature card with SVG icon or Emoji icon."""
    st.markdown(
        f"""
        <div class="custom-card">
            <div class="feature-icon-wrapper">
                {icon}
            </div>
            <div class="card-title">{title}</div>
            <div class="card-desc">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def technology_card(icon, title, subtitle):
    st.markdown(
        f"""
        <div class="custom-card" style="text-align: center;">
            <div class="feature-icon-wrapper" style="margin: 0 auto 1rem auto;">
                {icon}
            </div>
            <div class="card-title" style="font-size: 1.1rem;">{title}</div>
            <div class="card-desc" style="font-size: 0.85rem; font-weight: 600; color: #2563EB;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def metric_card(label, value, delta=None):
    st.metric(label, value, delta=delta)

def render_grade_badge(grade_str):
    css_class = "grade-good"
    if "Excellent" in grade_str:
        css_class = "grade-excellent"
    elif "Good" in grade_str:
        css_class = "grade-good"
    elif "Moderate" in grade_str:
        css_class = "grade-moderate"
    elif "Needs" in grade_str:
        css_class = "grade-needs-imp"

    return f'<span class="grade-badge {css_class}">{grade_str}</span>'