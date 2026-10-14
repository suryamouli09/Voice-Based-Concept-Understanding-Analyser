import streamlit as st

def hero(badge_text, title, description):
    st.markdown(
        f"""
        <div class="hero-banner">
            <span class="hero-badge">{badge_text}</span>
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def section_header(title, subtitle=""):
    st.markdown(
        f"""
        <div style="margin-top: 1.5rem; margin-bottom: 1rem;">
            <h2 style="font-size: 1.6rem; margin-bottom: 0.2rem;">{title}</h2>
            {f'<p style="color: #64748B; margin-top: 0; font-size: 0.95rem;">{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

def divider():
    st.divider()

def footer():
    st.markdown(
        """
        <div class="custom-footer">
            <p>© 2026 Voice Based Concept Understanding Analyser | Enterprise AI Speech Intelligence Platform</p>
            <p style="margin-top: 4px; font-size: 0.78rem;">Powered by OpenAI Whisper • Sentence-BERT • Librosa Audio DSP • Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True
    )