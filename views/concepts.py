import json
import streamlit as st
from pathlib import Path
from utils.helper import load_reference_concepts

def render_concepts():
    st.markdown(
        """
        <div class="app-header">
            <span class="header-badge">Knowledge Repository</span>
            <h1 class="header-title">Benchmark Concept Knowledge Base</h1>
            <p class="header-subtitle">Explore pre-configured evaluation ground-truth benchmarks or define new technical topics for candidate evaluation.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    concepts = load_reference_concepts()

    col_view, col_add = st.columns([1.6, 1])

    with col_view:
        st.subheader("📖 Active Benchmark Concepts")
        for topic_name, topic_data in concepts.items():
            with st.container(border=True):
                st.markdown(f"### 🎯 {topic_name}")
                st.markdown(f"**Domain Summary:** {topic_data.get('description', '')}")
                st.markdown(
                    f"""
                    <div class="benchmark-box" style="margin-top: 8px;">
                        <strong>Ground Truth Reference Text:</strong><br>
                        <em>"{topic_data.get('reference_text', '')}"</em>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with col_add:
        with st.container(border=True):
            st.subheader("➕ Add New Concept")
            st.caption("Expand the evaluation scope by registering custom technical concepts.")

            new_title = st.text_input("Concept Name:", placeholder="e.g. Distributed Consensus")
            new_desc = st.text_input("Summary Description:", placeholder="e.g. Raft and Paxos algorithms")
            new_ref = st.text_area(
                "Benchmark Ground Truth Definition:",
                placeholder="Write the ideal explanation that candidate spoken answers will be semantically compared against...",
                height=150
            )

            if st.button("Save New Benchmark Concept", type="primary", use_container_width=True):
                if new_title.strip() and new_ref.strip():
                    concepts[new_title.strip()] = {
                        "description": new_desc.strip(),
                        "reference_text": new_ref.strip()
                    }
                    concept_file = Path("models/reference_concepts.json")
                    with open(concept_file, "w", encoding="utf-8") as f:
                        json.dump(concepts, f, indent=4)
                    st.success(f"✅ Successfully registered benchmark topic '{new_title}'!")
                    st.rerun()
                else:
                    st.error("Please provide both a Concept Name and Ground Truth Definition.")

render_concepts()
