import os
import re
import streamlit as st
from pathlib import Path

from utils.helper import load_reference_concepts
from database.db import save_evaluation

from modules.audio_utils import save_uploaded_audio, generate_waveform
from modules.speech_to_text import transcribe_audio
from modules.feature_extractor import extract_audio_features
from modules.filler_word import analyze_filler_words
from modules.semantic_eval import semantic_similarity
from modules.scoring_engine import calculate_final_score
from modules.feedback_engine import generate_feedback
from modules.report_generator import generate_pdf_report
from modules.dashboard import score_gauge, score_bar, radar_score_chart, filler_words_pie

def render_tier_badge(grade_str: str) -> str:
    """Renders a styled tier badge."""
    css_class = "tier-competent"
    symbol = "🟡"
    if "Advanced" in grade_str or "Excellent" in grade_str:
        css_class = "tier-advanced"
        symbol = "🟢"
    elif "Competent" in grade_str or "Good" in grade_str:
        css_class = "tier-competent"
        symbol = "🟡"
    elif "Developing" in grade_str or "Moderate" in grade_str:
        css_class = "tier-developing"
        symbol = "🟠"
    elif "Needs" in grade_str:
        css_class = "tier-needs-focus"
        symbol = "🔴"

    return f'<div style="text-align:center;"><span class="tier-badge {css_class}">{symbol} {grade_str}</span></div>'

def render_evaluator():
    # Header Banner
    st.markdown(
        """
        <div class="app-header">
            <span class="header-badge">AI Speech Analytics Engine</span>
            <h1 class="header-title">Voice Concept Understanding Evaluator</h1>
            <p class="header-subtitle">Evaluate spoken technical explanations through OpenAI Whisper transcription, Sentence-BERT semantic alignment, and Librosa acoustic signal processing.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    concepts = load_reference_concepts()
    concept_names = list(concepts.keys())

    # Step 1: Benchmark Concept Selection
    col_concept, col_mode = st.columns([1.6, 1])

    with col_concept:
        selected_concept = st.selectbox(
            "🎯 Select Target Benchmark Concept:",
            concept_names,
            index=0,
            help="Choose the subject matter you are explaining."
        )
    
    with col_mode:
        st.write("")
        st.write("")
        show_benchmark = st.toggle("Show Benchmark Reference Definition", value=True)

    if show_benchmark and selected_concept:
        c_info = concepts[selected_concept]
        st.markdown(
            f"""
            <div class="benchmark-box">
                <strong style="color: #60A5FA;">Expected Benchmark Concept ({selected_concept}):</strong><br>
                <em>"{c_info.get('reference_text', '')}"</em>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # Step 2: Voice Input
    st.subheader("🎙️ Voice Input")
    
    tab_mic, tab_upload, tab_sample = st.tabs([
        "🎙️ Record Live Voice",
        "📁 Upload Audio File",
        "⚡ Quick Demo Presets"
    ])

    audio_path = None
    audio_source_label = "voice_input.wav"

    with tab_mic:
        st.caption("Record your spoken explanation directly via your microphone.")
        mic_audio = st.audio_input("Click to record explanation:")
        if mic_audio:
            os.makedirs("uploads", exist_ok=True)
            audio_path = os.path.join("uploads", "live_recording.wav")
            with open(audio_path, "wb") as f:
                f.write(mic_audio.getbuffer())
            audio_source_label = "live_mic_recording.wav"

    with tab_upload:
        st.caption("Upload a pre-recorded audio file (WAV, MP3, M4A, OGG).")
        uploaded_file = st.file_uploader(
            "Choose audio file",
            type=["wav", "mp3", "m4a", "ogg"],
            label_visibility="collapsed"
        )
        if uploaded_file:
            audio_path = save_uploaded_audio(uploaded_file)
            audio_source_label = uploaded_file.name

    with tab_sample:
        st.caption("Don't have audio ready? Test the full pipeline with built-in speech samples:")
        c_s1, c_s2 = st.columns(2)
        with c_s1:
            if st.button("🚀 Load Sample: Machine Learning (Fluent)", use_container_width=True):
                st.session_state["preset_audio"] = "data/samples/sample_machine_learning.wav"
                st.session_state["preset_topic"] = "Machine Learning"
                st.session_state["preset_name"] = "sample_machine_learning.wav"

        with c_s2:
            if st.button("☁️ Load Sample: Cloud Computing (With Fillers)", use_container_width=True):
                st.session_state["preset_audio"] = "data/samples/sample_cloud_computing.wav"
                st.session_state["preset_topic"] = "Cloud Computing"
                st.session_state["preset_name"] = "sample_cloud_computing.wav"

        if "preset_audio" in st.session_state and os.path.exists(st.session_state["preset_audio"]):
            audio_path = st.session_state["preset_audio"]
            audio_source_label = st.session_state.get("preset_name", "sample.wav")
            st.success(f"Loaded Preset: `{audio_source_label}`")

    # Audio Preview
    if audio_path and os.path.exists(audio_path):
        with st.container(border=True):
            st.markdown(f"**🔊 Audio Preview:** `{audio_source_label}`")
            st.audio(audio_path)

        # Trigger Button
        analyze_btn = st.button("🚀 Run AI Conceptual Evaluation", type="primary", use_container_width=True)
    else:
        analyze_btn = False
        st.info("👆 Please record your voice, upload an audio file, or click a Quick Demo Preset above to proceed.")

    # Execution Pipeline
    if analyze_btn and audio_path:
        with st.status("🧠 Processing Multi-Modal Speech Evaluation...", expanded=True) as status:
            st.write("🎙️ [1/5] Transcribing speech using OpenAI Whisper...")
            transcript = transcribe_audio(audio_path)

            st.write("🎧 [2/5] Extracting acoustic DSP features (WPM, pitch, pauses) via Librosa...")
            features = extract_audio_features(audio_path, transcript)
            waveform_path = generate_waveform(audio_path)

            st.write("💬 [3/5] Detecting speech hesitations and filler word patterns...")
            filler_result = analyze_filler_words(transcript)

            st.write("🧠 [4/5] Computing Sentence-BERT dense vector semantic alignment...")
            benchmark_text = concepts[selected_concept]["reference_text"]
            semantic_result = semantic_similarity(transcript, benchmark_text)

            st.write("📊 [5/5] Synthesizing multidimensional score and generating report...")
            score_result = calculate_final_score(features, filler_result, semantic_result)
            feedback = generate_feedback(score_result, filler_result, features, transcript, benchmark_text)

            pdf_report_path = generate_pdf_report(
                topic=selected_concept,
                transcript=transcript,
                features=features,
                filler_result=filler_result,
                semantic_result=semantic_result,
                score_result=score_result,
                strengths=feedback["strengths"],
                suggestions=feedback["suggestions"],
                waveform_path=waveform_path
            )

            # Save in SQLite
            save_evaluation(
                filename=audio_source_label,
                concept_name=selected_concept,
                overall_score=score_result["Final Score"],
                grade=score_result["Grade"],
                semantic_score=score_result["Semantic Score"],
                fluency_score=score_result["Fluency Score"],
                communication_score=score_result["Communication Score"],
                transcript=transcript,
                filler_count=filler_result["Filler Count"],
                pdf_report_path=pdf_report_path,
                meta_dict={
                    "fillers": filler_result["Detected Fillers"],
                    "wpm": features["Speech Rate"],
                    "matched_keywords": feedback["matched_keywords"]
                }
            )

            # Store in session state for persistence
            st.session_state["latest_results"] = {
                "concept": selected_concept,
                "transcript": transcript,
                "features": features,
                "filler_result": filler_result,
                "semantic_result": semantic_result,
                "score_result": score_result,
                "feedback": feedback,
                "waveform_path": waveform_path,
                "pdf_path": pdf_report_path
            }

            status.update(label="✅ Conceptual Evaluation Complete!", state="complete", expanded=False)

    # Render Results Section
    if "latest_results" in st.session_state:
        res = st.session_state["latest_results"]
        scores = res["score_result"]
        sem = res["semantic_result"]
        feats = res["features"]
        fillers = res["filler_result"]
        fb = res["feedback"]

        st.markdown("---")
        st.subheader("📊 Evaluation Dashboard & Assessment Results")

        # Top Executive Summary Row
        col_g, col_kpi, col_chart = st.columns([1.2, 1, 1.4])

        with col_g:
            with st.container(border=True):
                st.plotly_chart(score_gauge(scores["Final Score"]), use_container_width=True)
                st.markdown(render_tier_badge(scores["Grade"]), unsafe_allow_html=True)
                st.write("")

        with col_kpi:
            with st.container(border=True):
                st.metric("🧠 Semantic Match", f"{scores['Semantic Score']}%", help="Cosine similarity with benchmark definition.")
                st.metric("🗣️ Speaking Cadence", f"{scores['Fluency Score']}%", delta=f"{feats['Speech Rate']} WPM")
                st.metric("💬 Articulation Polish", f"{scores['Communication Score']}%", delta=f"{fillers['Filler Count']} Fillers", delta_color="inverse")

        with col_chart:
            with st.container(border=True):
                st.plotly_chart(score_bar(scores), use_container_width=True)

        # Tabs for In-Depth Analytics
        tab_trans, tab_skills, tab_acoustic, tab_coach, tab_export = st.tabs([
            "📝 Transcript & Fillers",
            "🕸️ Competency Radar",
            "🎧 Acoustic Dynamics",
            "💡 AI Diagnostic Coaching",
            "📄 Official PDF Report"
        ])

        # Tab 1: Transcript & Fillers
        with tab_trans:
            c_t1, c_t2 = st.columns([1.8, 1])
            with c_t1:
                st.markdown("#### Spoken Explanation Transcript")
                raw_tr = res["transcript"]
                highlighted_tr = raw_tr
                # Highlight detected fillers
                for word in fillers.get("Detected Fillers", {}).keys():
                    pattern = re.compile(r"\b(" + re.escape(word) + r")\b", re.IGNORECASE)
                    highlighted_tr = pattern.sub(r'<span class="filler-tag">\1</span>', highlighted_tr)

                st.markdown(
                    f'<div class="transcript-card">{highlighted_tr if highlighted_tr else "No transcript detected."}</div>',
                    unsafe_allow_html=True
                )
                st.caption("🚩 Words highlighted in red are detected verbal crutches or fillers.")

            with c_t2:
                st.markdown("#### Filler Words Breakdown")
                f_count = fillers["Filler Count"]
                f_ratio = fillers["Filler Ratio"]
                st.write(f"Total Words Spoken: **{fillers['Total Words']}**")
                st.write(f"Fillers Flagged: **{f_count}** ({f_ratio}%)")

                if fillers["Detected Fillers"]:
                    st.plotly_chart(filler_words_pie(fillers["Detected Fillers"]), use_container_width=True)
                else:
                    st.success("🎉 Flawless! Zero filler words detected.")

        # Tab 2: Competency Radar
        with tab_skills:
            c_r1, c_r2 = st.columns([1.4, 1])
            with c_r1:
                st.markdown("#### Multi-Axial Competence Profile")
                st.plotly_chart(
                    radar_score_chart(
                        scores["Semantic Score"],
                        scores["Fluency Score"],
                        scores["Communication Score"],
                        acoustic_stability=80.0
                    ),
                    use_container_width=True
                )
            with c_r2:
                st.markdown("#### Competence Dimensions")
                st.markdown(f"- **Semantic Alignment ({scores['Semantic Score']}%):** Directness and technical depth compared to reference.")
                st.markdown(f"- **Speech Cadence ({scores['Fluency Score']}%):** Speaking speed consistency ({feats['Speech Rate']} WPM).")
                st.markdown(f"- **Articulation ({scores['Communication Score']}%):** Confidence and hesitation control.")
                st.markdown(f"- **Acoustic Balance:** Energy and pitch consistency.")

        # Tab 3: Acoustic Dynamics
        with tab_acoustic:
            a1, a2, a3, a4 = st.columns(4)
            a1.metric("Duration", f"{feats['Duration']} s")
            a2.metric("Speech Rate", f"{feats['Speech Rate']} WPM", help="Optimal technical rate: 115-165 WPM")
            a3.metric("Pause Ratio", f"{feats['Pause Ratio']*100:.1f}%")
            a4.metric("Mean Pitch", f"{feats['Pitch']} Hz")

            st.markdown("#### Acoustic Waveform Visual")
            if res.get("waveform_path") and os.path.exists(res["waveform_path"]):
                st.image(res["waveform_path"], use_container_width=True)

        # Tab 4: AI Coaching
        with tab_coach:
            col_str, col_sug = st.columns(2)
            with col_str:
                with st.container(border=True):
                    st.markdown("### 🌟 Demonstrated Strengths")
                    for st_item in fb["strengths"]:
                        st.markdown(f"- ✅ **{st_item}**")

            with col_sug:
                with st.container(border=True):
                    st.markdown("### 🎯 Recommendations for Growth")
                    for sug_item in fb["suggestions"]:
                        st.markdown(f"- 💡 **{sug_item}**")

            # Keyword Comparison
            st.markdown("#### 🔍 Technical Vocabulary Alignment")
            c_k1, c_k2 = st.columns(2)
            with c_k1:
                st.write("**Matched Key Concepts:**")
                if fb["matched_keywords"]:
                    chips = "".join([f'<span class="keyword-chip">{kw}</span>' for kw in fb["matched_keywords"]])
                    st.markdown(chips, unsafe_allow_html=True)
                else:
                    st.caption("No key vocabulary matches identified.")

            with c_k2:
                st.write("**Suggested Keywords to Incorporate:**")
                if fb["missed_keywords"]:
                    chips_m = "".join([f'<span class="keyword-chip-missed">{kw}</span>' for kw in fb["missed_keywords"]])
                    st.markdown(chips_m, unsafe_allow_html=True)
                else:
                    st.caption("Excellent coverage of key reference vocabulary.")

        # Tab 5: PDF Report Export
        with tab_export:
            st.markdown("#### Official PDF Assessment Report")
            st.caption("Download a standardized, formal PDF assessment summary including charts, transcripts, and scores.")
            pdf_path = res.get("pdf_path")
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                st.download_button(
                    label="📥 Download Official Assessment Report (PDF)",
                    data=pdf_bytes,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    type="primary"
                )
                st.success(f"Report Generated: `{os.path.basename(pdf_path)}`")
            else:
                st.warning("PDF report is not available.")

render_evaluator()
