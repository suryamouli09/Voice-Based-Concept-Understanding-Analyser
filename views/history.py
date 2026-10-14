import os
import streamlit as st
import pandas as pd
from database.db import get_all_evaluations, delete_evaluation, clear_all_history

def render_history():
    st.markdown(
        """
        <div class="app-header">
            <span class="header-badge">Audit & Records</span>
            <h1 class="header-title">Assessment History & Records Log</h1>
            <p class="header-subtitle">Search, inspect, and re-download previously completed voice conceptual evaluations stored securely in the database.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    evaluations = get_all_evaluations()

    if not evaluations:
        st.info("ℹ️ Evaluation history is currently empty. Run an evaluation in the **Voice Evaluator** workspace to record results here.")
        return

    # Search & Filter Controls
    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])

    with col_s1:
        search_query = st.text_input("🔍 Search by concept name, filename, or transcript keyword:", "")

    with col_s2:
        grade_options = ["All Performance Tiers", "Advanced", "Competent", "Developing", "Needs"]
        grade_filter = st.selectbox("Filter Tier:", grade_options)

    with col_s3:
        st.write("")
        st.write("")
        if st.button("🗑️ Clear Entire History", type="secondary"):
            clear_all_history()
            st.rerun()

    # Filter Records
    filtered_evals = []
    for item in evaluations:
        tr_text = item.get("transcript") or ""
        concept_name = item.get("concept_name") or ""
        fname = item.get("filename") or ""
        grade = item.get("grade") or ""

        match_search = (
            not search_query or
            search_query.lower() in concept_name.lower() or
            search_query.lower() in fname.lower() or
            search_query.lower() in tr_text.lower()
        )

        match_grade = (
            grade_filter == "All Performance Tiers" or
            grade_filter.lower() in grade.lower()
        )

        if match_search and match_grade:
            filtered_evals.append(item)

    st.caption(f"Showing {len(filtered_evals)} of {len(evaluations)} evaluation records.")
    st.markdown("---")

    for rec in filtered_evals:
        with st.expander(
            f"📅 {rec['timestamp']}  |  🎯 {rec['concept_name']}  |  🏆 Score: {rec['overall_score']:.1f}/100  |  {rec['grade']}",
            expanded=False
        ):
            c1, c2, c3 = st.columns([1.5, 1.2, 1])

            with c1:
                st.markdown(f"**Audio File:** `{rec['filename']}`")
                st.markdown(f"**Performance Rating:** {rec['grade']}")
                st.markdown(f"**Filler Words Detected:** `{rec['filler_count']}`")

            with c2:
                st.markdown("**Component Scores:**")
                st.write(f"- Semantic Alignment: **{rec['semantic_score']:.1f}%**")
                st.write(f"- Speech Cadence / Fluency: **{rec['fluency_score']:.1f}%**")
                st.write(f"- Articulation Clarity: **{rec['communication_score']:.1f}%**")

            with c3:
                pdf_path = rec.get("pdf_report_path")
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        pdf_data = f.read()
                    st.download_button(
                        label="📥 Re-download PDF",
                        data=pdf_data,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf",
                        key=f"dl_hist_{rec['id']}"
                    )
                else:
                    st.caption("PDF file not available.")

                if st.button("❌ Delete Record", key=f"del_hist_{rec['id']}"):
                    delete_evaluation(rec["id"])
                    st.rerun()

            st.markdown("**Transcript:**")
            st.markdown(
                f'<div class="transcript-card" style="font-size: 0.92rem; padding: 0.9rem;">{rec["transcript"]}</div>',
                unsafe_allow_html=True
            )

render_history()
