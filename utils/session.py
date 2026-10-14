import streamlit as st


def initialize_session():

    defaults = {

        "transcript": "",

        "features": {},

        "filler_result": {},

        "semantic_result": {},

        "score_result": {},

        "strengths": [],

        "suggestions": [],

        "pdf_path": None,

        "analysis_done": False

    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value