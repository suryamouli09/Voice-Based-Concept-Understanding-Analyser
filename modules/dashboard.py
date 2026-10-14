import plotly.graph_objects as go
import plotly.express as px

def score_gauge(score: float):
    """Creates a modern circular score gauge with performance color zones."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={'suffix': "", 'font': {'size': 44, 'family': 'Inter, sans-serif', 'color': '#F9FAFB'}},
        title={'text': "Overall Concept Mastery", 'font': {'size': 15, 'color': '#9CA3AF'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#4B5563"},
            'bar': {'color': "#3B82F6", 'thickness': 0.28},
            'bgcolor': "#1F2937",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.20)"},
                {'range': [50, 70], 'color': "rgba(245, 158, 11, 0.20)"},
                {'range': [70, 85], 'color': "rgba(59, 130, 246, 0.20)"},
                {'range': [85, 100], 'color': "rgba(16, 185, 129, 0.20)"}
            ]
        }
    ))

    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def score_bar(score_result: dict):
    """Bar chart comparing core evaluation pillars."""
    categories = ["Semantic Match", "Fluency & Pace", "Clarity & Fillers"]
    scores = [
        score_result.get("Semantic Score", 0.0),
        score_result.get("Fluency Score", 0.0),
        score_result.get("Communication Score", 0.0)
    ]
    colors = ['#3B82F6', '#8B5CF6', '#10B981']

    fig = go.Figure(go.Bar(
        x=categories,
        y=scores,
        text=[f"{s:.1f}%" for s in scores],
        textposition='outside',
        textfont=dict(color="#F3F4F6", size=13, family="Inter"),
        marker=dict(color=colors, line=dict(width=0)),
        width=0.45
    ))

    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=30, b=30),
        yaxis=dict(range=[0, 115], showgrid=True, gridcolor='#1F2937', zeroline=False),
        xaxis=dict(showgrid=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9CA3AF", family="Inter, sans-serif")
    )
    return fig

def radar_score_chart(semantic: float, fluency: float, communication: float, acoustic_stability: float = 75.0):
    """Radar chart for multi-dimensional skill evaluation."""
    categories = ['Semantic Alignment', 'Speech Cadence', 'Articulation Clarity', 'Acoustic Balance']
    values = [semantic, fluency, communication, acoustic_stability]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.22)',
        line=dict(color='#60A5FA', width=2),
        name='Candidate Profile'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='#374151', tickfont=dict(color="#9CA3AF", size=10)),
            angularaxis=dict(gridcolor='#374151', tickfont=dict(color="#F9FAFB", size=11))
        ),
        showlegend=False,
        height=280,
        margin=dict(l=40, r=40, t=25, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif")
    )
    return fig

def filler_words_pie(filler_counts: dict):
    """Donut chart for detected filler words breakdown."""
    if not filler_counts:
        fig = go.Figure()
        fig.add_annotation(text="Zero Fillers Detected! 🎉", showarrow=False, font=dict(size=14, color="#10B981"))
        fig.update_layout(height=240, paper_bgcolor="rgba(0,0,0,0)")
        return fig

    labels = list(filler_counts.keys())
    values = list(filler_counts.values())

    fig = px.pie(
        names=labels,
        values=values,
        hole=0.5,
        color_discrete_sequence=['#F87171', '#FB923C', '#FBBF24', '#C084FC', '#60A5FA']
    )

    fig.update_traces(textposition='inside', textinfo='label+percent')
    fig.update_layout(
        height=240,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F9FAFB", family="Inter, sans-serif"),
        showlegend=False
    )
    return fig