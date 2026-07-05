import streamlit as st

from utils.helper import load_reference_concepts
from modules.audio_utils import (
    save_uploaded_audio,
    get_audio_info,
    generate_waveform
)
from modules.speech_to_text import transcribe_audio
from modules.filler_word import analyze_filler_words
from modules.semantic_eval import semantic_similarity
from modules.scoring_engine import calculate_final_score
from modules.dashboard import score_gauge, score_bar
from modules.feedback_engine import generate_feedback
from modules.report_generator import generate_pdf_report
from modules.feature_extractor import extract_audio_features


# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------

st.set_page_config(
    page_title="Voice Based Concept Understanding Analyser",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 Voice Based Concept Understanding Analyser")
st.markdown("---")

# ---------------------------------------------------
# Load Concepts
# ---------------------------------------------------

concepts = load_reference_concepts()

left, right = st.columns([2, 1])

# ===================================================
# LEFT PANEL
# ===================================================

with left:

    st.header("Upload Audio")

    uploaded_audio = st.file_uploader(
        "Choose an audio file",
        type=["wav", "mp3", "m4a"]
    )

    if uploaded_audio:

        # Save uploaded audio
        file_path = save_uploaded_audio(uploaded_audio)

        # Audio information
        size, duration = get_audio_info(file_path)

        # Generate waveform
        waveform = generate_waveform(file_path)

        st.success("Audio Uploaded Successfully")

        st.audio(uploaded_audio)

        c1, c2 = st.columns(2)

        with c1:
            st.metric("File Size", f"{size} MB")

        with c2:
            st.metric("Duration", f"{duration} sec")

        st.subheader("📈 Audio Waveform")

        st.image(
            waveform,
            caption="Audio Waveform",
            width=900
        )

# ===================================================
# RIGHT PANEL
# ===================================================

with right:

    st.header("Reference Concept")

    selected_concept = st.selectbox(
        "Select Topic",
        list(concepts.keys())
    )

    st.info(concepts[selected_concept]["description"])

# ===================================================
# ANALYZE BUTTON
# ===================================================

if uploaded_audio:

    st.markdown("---")

    if st.button("🚀 Analyze Concept", width="stretch"):

        with st.spinner("Analyzing audio..."):

            # Whisper Transcription
            transcript = transcribe_audio(file_path)

            # Audio Features
            features = extract_audio_features(
                file_path,
                transcript
            )
            filler_result = analyze_filler_words(transcript)
            reference_text = concepts[selected_concept]["reference_text"]

            semantic_result = semantic_similarity(
            transcript,
            reference_text
            )
            score_result = calculate_final_score(
            features,
            filler_result,
            semantic_result
            )
            strengths, suggestions = generate_feedback(
            score_result,
            filler_result
            )
            pdf_path = generate_pdf_report(
                selected_concept,
                transcript,
                features,
                filler_result,
                semantic_result,
                score_result,
                strengths,
                suggestions
            )

            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_file,
                    file_name="VBCUA_Report.pdf",
                    mime="application/pdf"
                )
            st.success("Analysis Completed Successfully!")

        # --------------------------------------------
        # Transcript
        # --------------------------------------------

        st.subheader("📝 Transcript")

        st.write(transcript)

        # --------------------------------------------
        # Audio Features
        # --------------------------------------------

        st.markdown("---")

        st.subheader("🎤 Audio Feature Analysis")

        col1, col2 = st.columns(2)

        items = list(features.items())

        half = (len(items) + 1) // 2

        with col1:

            for key, value in items[:half]:
                st.metric(key, value)

        with col2:

            for key, value in items[half:]:
                st.metric(key, value)

        st.markdown("---")

        st.subheader("💬 Filler Word Analysis")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
             "Total Words",
            filler_result["Total Words"]
         )

        st.metric(
        "Filler Count",
        filler_result["Filler Count"]
        )

        st.metric(
        "Filler Ratio (%)",
        filler_result["Filler Ratio"]
        )

        with col2:

         st.write("### Detected Fillers")

        if filler_result["Detected Fillers"]:

            for word, count in filler_result["Detected Fillers"].items():
                st.write(f"• **{word}** : {count}")

        else:
            st.success("No filler words detected 🎉")

        st.markdown("---")

        st.subheader("🧠 Concept Understanding Analysis")

        col1, col2 = st.columns(2)

        with col1:

         st.metric(
        "Semantic Similarity (%)",
        semantic_result["Similarity"]
         )

        with col2:

            st.metric(
        "Understanding Level",
        semantic_result["Level"]
        )
            
        st.markdown("---")

        st.subheader("🏆 Final Evaluation")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
        "Overall Score",
        f"{score_result['Final Score']} / 100"
        )

        st.metric(
        "Grade",
        score_result["Grade"]
        )

        with col2:

            st.metric(
        "Semantic Score",
        score_result["Semantic Score"]
        )

        st.metric(
        "Fluency Score",
        score_result["Fluency Score"]
        )

        st.metric(
        "Communication Score",
        score_result["Communication Score"]
        )

        st.markdown("---")

        st.subheader("📊 Performance Dashboard")

        left, right = st.columns(2)

        with left:

            gauge = score_gauge(
        score_result["Final Score"]
        )

        st.plotly_chart(
        gauge,
        use_container_width=True
        )

        with right:

            bar = score_bar(score_result)

            st.plotly_chart(
            bar,
            use_container_width=True
            )

        st.markdown("---")

        st.subheader("🤖 AI Feedback")

        left, right = st.columns(2)

        with left:

            st.success("Strengths")

        for s in strengths:
            st.write(f"✅ {s}")

        with right:

            st.warning("Suggestions")

        if suggestions:
            for s in suggestions:
                st.write(f"• {s}")
        else:
         st.write("Excellent performance. Keep practicing!")