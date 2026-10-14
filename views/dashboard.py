import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import get_all_evaluations, get_evaluation_stats
from modules.dashboard import radar_score_chart

def render_dashboard():
    st.markdown(
        """
        <div class="app-header">
            <span class="header-badge">Performance Intelligence</span>
            <h1 class="header-title">Analytics & Assessment Dashboard</h1>
            <p class="header-subtitle">Aggregate metrics, candidate score distributions, and longitudinal fluency trends across all conceptual voice evaluations.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    evaluations = get_all_evaluations()
    stats = get_evaluation_stats()

    # KPI Top Row
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("📊 Total Evaluations", stats["total_evaluations"])
    k2.metric("🏆 Mean Mastery Score", f"{stats['avg_overall']:.1f}/100" if stats["avg_overall"] else "N/A")
    k3.metric("🧠 Avg Semantic Match", f"{stats['avg_semantic']:.1f}%" if stats["avg_semantic"] else "N/A")
    k4.metric("🗣️ Avg Fluency Score", f"{stats['avg_fluency']:.1f}%" if stats["avg_fluency"] else "N/A")
    k5.metric("💬 Total Fillers Flagged", stats["total_fillers"])

    st.markdown("---")

    if not evaluations:
        st.info("ℹ️ No evaluations recorded yet. Run an evaluation in the **Voice Evaluator** workspace to populate analytics charts.")
        return

    df = pd.DataFrame(evaluations)

    # Filter Controls
    col_filter, col_spacer = st.columns([1.5, 2])
    with col_filter:
        topics = ["All Topics"] + sorted(list(df["concept_name"].unique()))
        selected_topic = st.selectbox("Filter Analytics by Benchmark Concept:", topics)

    filtered_df = df if selected_topic == "All Topics" else df[df["concept_name"] == selected_topic]

    # Row 1 Charts: Progression & Grade Distribution
    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.markdown("#### 📈 Longitudinal Score History")
            fig_line = px.line(
                filtered_df,
                x="timestamp",
                y="overall_score",
                color="concept_name",
                markers=True,
                labels={"timestamp": "Date & Time", "overall_score": "Score (0-100)"}
            )
            fig_line.update_layout(
                height=300,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(range=[0, 105], gridcolor="#1F2937"),
                xaxis=dict(gridcolor="#1F2937"),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_line, use_container_width=True)

    with c2:
        with st.container(border=True):
            st.markdown("#### 🎯 Performance Tier Distribution")
            fig_pie = px.pie(
                filtered_df,
                names="grade",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_pie.update_layout(
                height=300,
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=True
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # Row 2 Charts: Topic Breakdown & Radar Profile
    c3, c4 = st.columns(2)

    with c3:
        with st.container(border=True):
            st.markdown("#### 📊 Topic-wise Competence Sub-Scores")
            avg_by_topic = df.groupby("concept_name")[["semantic_score", "fluency_score", "communication_score"]].mean().reset_index()

            fig_bar = px.bar(
                avg_by_topic,
                x="concept_name",
                y=["semantic_score", "fluency_score", "communication_score"],
                barmode="group",
                labels={"value": "Mean Score (%)", "concept_name": "Concept Topic", "variable": "Metric"}
            )
            fig_bar.update_layout(
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(range=[0, 110], gridcolor="#1F2937"),
                xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                margin=dict(l=10, r=10, t=20, b=10)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    with c4:
        with st.container(border=True):
            st.markdown("#### 🕸️ Cohort Competency Profile")
            avg_sem = float(filtered_df["semantic_score"].mean()) if not filtered_df.empty else 0.0
            avg_flu = float(filtered_df["fluency_score"].mean()) if not filtered_df.empty else 0.0
            avg_com = float(filtered_df["communication_score"].mean()) if not filtered_df.empty else 0.0
            
            radar_fig = radar_score_chart(avg_sem, avg_flu, avg_com, acoustic_stability=75.0)
            st.plotly_chart(radar_fig, use_container_width=True)

render_dashboard()
