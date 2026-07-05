import os
from datetime import datetime
from pydoc import doc
from pyexpat import features
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    Image,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet
from streamlit import table


def generate_pdf_report(
        topic,
        transcript,
        features,
        filler_result,
        semantic_result,
        score_result,
        strengths,
        suggestions,
):

    os.makedirs("outputs/reports", exist_ok=True)

    pdf_path = "outputs/reports/VBCUA_Report.pdf"

    styles = getSampleStyleSheet()

    current_date = datetime.now().strftime("%d-%m-%Y %H:%M")

    doc = SimpleDocTemplate(pdf_path)

    story = []

    # -----------------------------
    # Title
    # -----------------------------

    story.append(
        Paragraph(
            "<b>Voice Based Concept Understanding Analyser</b>",
            styles["Title"]
        )
    )
    story.append(Spacer(1,20))

    story.append(
    Paragraph(
        f"<b>Date & Time:</b> {current_date}",
        styles["BodyText"]
    )
)

    story.append(Spacer(1,12))

    # -----------------------------
    # Topic
    # -----------------------------

    story.append(
        Paragraph(
            f"<b>Reference Topic:</b> {topic}",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1,12))

    # -----------------------------
    # Transcript
    # -----------------------------

    story.append(
        Paragraph(
            "<b>Transcript</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            transcript,
            styles["BodyText"]
        )
    )

    story.append(Spacer(1,15))

    # -----------------------------
    # Audio Features
    # -----------------------------

    story.append(
        Paragraph(
            "<b>Audio Features</b>",
            styles["Heading2"]
        )
    )

    feature_data = [
    ["Feature", "Value"]
]

    for key, value in features.items():
        feature_data.append([key, str(value)])

    table = Table(feature_data)

    table.setStyle(TableStyle([

    ('BACKGROUND', (0,0), (-1,0), colors.darkblue),

    ('TEXTCOLOR', (0,0), (-1,0), colors.white),

    ('GRID', (0,0), (-1,-1), 1, colors.grey),

    ('BACKGROUND', (0,1), (-1,-1), colors.beige),

    ('BOTTOMPADDING', (0,0), (-1,0), 10)

]))

    story.append(table)

    story.append(Spacer(1,20))  

    story.append(
    Paragraph(
        "<b>Waveform</b>",
        styles["Heading2"]
    )
)

    story.append(Spacer(1,10))

    story.append(
    Image(
        "outputs/graphs/waveform.png",
        width=450,
        height=120
    )
)

    story.append(Spacer(1,20))

    # -----------------------------
    # Semantic Analysis
    # -----------------------------

    story.append(
        Paragraph(
            "<b>Semantic Similarity</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            f"Similarity : {semantic_result['Similarity']} %",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"Understanding : {semantic_result['Level']}",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1,15))

    # -----------------------------
    # Final Score
    # -----------------------------

    # -----------------------------
# Final Evaluation
# -----------------------------

    story.append(
    Paragraph(
        "<b>Final Evaluation</b>",
        styles["Heading2"]
    )
)

    story.append(Spacer(1,10))

    score_data = [

    ["Metric", "Score"],

    ["Semantic Score", score_result["Semantic Score"]],

    ["Fluency Score", score_result["Fluency Score"]],

    ["Communication Score", score_result["Communication Score"]],

    ["Final Score", score_result["Final Score"]],

    ["Grade", score_result["Grade"]]

]

    score_table = Table(score_data)

    score_table.setStyle(TableStyle([

    ('BACKGROUND',(0,0),(-1,0),colors.darkgreen),

    ('TEXTCOLOR',(0,0),(-1,0),colors.white),

    ('GRID',(0,0),(-1,-1),1,colors.grey),

    ('BACKGROUND',(0,1),(-1,-1),colors.whitesmoke),

    ('BOTTOMPADDING',(0,0),(-1,0),10)

]))

    story.append(score_table)

    story.append(Spacer(1,20))

    story.append(Spacer(1,15))

    # -----------------------------
    # Strengths
    # -----------------------------

    story.append(
        Paragraph(
            "<b>Strengths</b>",
            styles["Heading2"]
        )
    )

    for item in strengths:

        story.append(
            Paragraph(
                "• " + item,
                styles["BodyText"]
            )
        )

    story.append(Spacer(1,15))

    # -----------------------------
    # Suggestions
    # -----------------------------

    story.append(
        Paragraph(
            "<b>Suggestions</b>",
            styles["Heading2"]
        )
    )

    for item in suggestions:

        story.append(
            Paragraph(
                "• " + item,
                styles["BodyText"]
            )
        )

    story.append(Spacer(1,30))

    # -----------------------------
    # Footer
    # -----------------------------

    story.append(
    Paragraph(
        "<i>Generated by Voice Based Concept Understanding Analyser</i>",
        styles["Italic"]
    )
)

    doc.build(story)

    return pdf_path