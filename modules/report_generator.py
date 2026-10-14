import os
import re
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def _strip_emojis(text: str) -> str:
    """Removes emoji characters that cause rendering errors in standard PDF fonts."""
    if not text:
        return ""
    # Strip high surrogate / emoji unicode ranges
    emoji_pattern = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)
    cleaned = emoji_pattern.sub("", text)
    # Also strip common geometric shapes/colors like 🟢, 🟡, 🟠, 🔴
    cleaned = re.sub(r"[🟢🟡🟠🔴•💡✅🚀🎙️🧠🎧📊📄📜ℹ️📚]+", "", cleaned)
    return cleaned.strip()

def generate_pdf_report(
    topic: str,
    transcript: str,
    features: dict,
    filler_result: dict,
    semantic_result: dict,
    score_result: dict,
    strengths: list,
    suggestions: list,
    waveform_path: str = None
) -> str:
    """
    Generates a clean, professional PDF assessment report.
    Returns the file path to the generated PDF.
    """
    os.makedirs("outputs/reports", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_topic = re.sub(r'[^a-zA-Z0-9]', '_', topic)
    pdf_path = os.path.join("outputs", "reports", f"Assessment_{clean_topic}_{timestamp}.pdf")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=15
    )

    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=14,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155')
    )

    bullet_style = ParagraphStyle(
        'BulletItem',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B'),
        leftIndent=15,
        spaceAfter=4
    )

    story = []

    # Title & Metadata Header
    story.append(Paragraph("Voice-Based Concept Understanding Evaluation", title_style))
    current_time_str = datetime.now().strftime("%B %d, %Y - %I:%M %p")
    story.append(Paragraph(f"Official AI Assessment Report  |  Generated on {current_time_str}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=15))

    # Assessment Target & Summary Banner
    clean_grade = _strip_emojis(score_result.get("Grade", "Competent"))
    final_score = score_result.get("Final Score", 0.0)

    summary_table_data = [
        [
            Paragraph(f"<b>Benchmark Concept:</b> {topic}", body_style),
            Paragraph(f"<b>Overall Score:</b> <font color='#2563EB' size='12'><b>{final_score}/100</b></font>", body_style),
            Paragraph(f"<b>Performance Tier:</b> <b>{clean_grade}</b>", body_style)
        ]
    ]
    t_summary = Table(summary_table_data, colWidths=[200, 160, 160])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 10))

    # Score Pillars Breakdown Table
    story.append(Paragraph("Score Breakdown & Component Metrics", section_style))
    score_table_data = [
        ["Evaluation Pillar", "Weight", "Score", "Rating"],
        ["Semantic Conceptual Alignment", "60%", f"{score_result.get('Semantic Score', 0)}%", _strip_emojis(semantic_result.get('Level', 'Good'))],
        ["Fluency & Speech Cadence", "25%", f"{score_result.get('Fluency Score', 0)}%", f"{features.get('Speech Rate', 0)} WPM"],
        ["Communication & Articulation", "15%", f"{score_result.get('Communication Score', 0)}%", f"{filler_result.get('Filler Count', 0)} Fillers ({filler_result.get('Filler Ratio', 0)}%)"]
    ]
    t_scores = Table(score_table_data, colWidths=[180, 80, 100, 160])
    t_scores.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#FFFFFF')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_scores)
    story.append(Spacer(1, 10))

    # Transcribed Explanation
    story.append(Paragraph("Spoken Explanation Transcript", section_style))
    clean_tr = _strip_emojis(transcript) if transcript else "No transcript detected."
    t_transcript = Table([[Paragraph(clean_tr, body_style)]], colWidths=[520])
    t_transcript.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('LINELEFT', (0,0), (-1,-1), 3, colors.HexColor('#2563EB')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_transcript)
    story.append(Spacer(1, 10))

    # Acoustic Features Table
    story.append(Paragraph("Acoustic & Signal Processing Parameters", section_style))
    acoustic_data = [
        ["Duration", f"{features.get('Duration', 0)} seconds", "Mean Pitch", f"{features.get('Pitch', 0)} Hz"],
        ["Speech Rate", f"{features.get('Speech Rate', 0)} WPM", "Pause Ratio", f"{features.get('Pause Ratio', 0)*100:.1f}%"],
        ["RMS Energy", f"{features.get('RMS Energy', 0)}", "Zero Crossing", f"{features.get('Zero Crossing Rate', 0)}"]
    ]
    t_acoustic = Table(acoustic_data, colWidths=[130, 130, 130, 130])
    t_acoustic.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#F8FAFC')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_acoustic)

    # Waveform image if available
    wf_path = waveform_path or "outputs/graphs/waveform.png"
    if os.path.exists(wf_path):
        story.append(Spacer(1, 8))
        story.append(Image(wf_path, width=520, height=85))

    story.append(Spacer(1, 10))

    # Diagnostic Strengths & Suggestions
    story.append(Paragraph("AI Coaching Insights & Recommendations", section_style))
    
    story.append(Paragraph("<b>Demonstrated Strengths:</b>", body_style))
    for s in strengths:
        clean_s = _strip_emojis(s)
        story.append(Paragraph(f"+ {clean_s}", bullet_style))
    
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Targeted Recommendations for Improvement:</b>", body_style))
    for sug in suggestions:
        clean_sug = _strip_emojis(sug)
        story.append(Paragraph(f"- {clean_sug}", bullet_style))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94A3B8'), spaceAfter=8))
    story.append(Paragraph("Voice Based Concept Understanding Analyser | Automated Evaluation Report", subtitle_style))

    doc.build(story)
    return pdf_path