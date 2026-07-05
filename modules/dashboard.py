import plotly.graph_objects as go
import plotly.express as px


def score_gauge(score):

    fig = go.Figure(go.Indicator(

        mode="gauge+number",

        value=score,

        title={'text': "Overall Score"},

        gauge={

            'axis': {'range': [0, 100]},

            'bar': {'color': "darkblue"},

            'steps': [

                {'range': [0, 50], 'color': "#ffb3b3"},

                {'range': [50, 70], 'color': "#ffe699"},

                {'range': [70, 85], 'color': "#c9f7c9"},

                {'range': [85, 100], 'color': "#7CFC00"}

            ]
        }
    ))

    fig.update_layout(height=350)

    return fig


def score_bar(score_result):

    names = [

        "Semantic",

        "Fluency",

        "Communication"

    ]

    scores = [

        score_result["Semantic Score"],

        score_result["Fluency Score"],

        score_result["Communication Score"]

    ]

    fig = px.bar(

        x=names,

        y=scores,

        text=scores,

        title="Score Comparison"

    )

    fig.update_layout(height=350)

    return fig