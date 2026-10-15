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
from modules.feedback_engine import (
    generate_feedback,
    get_topic_prompts,
    get_topic_coach_answer,
    get_keyword_flashcard_fact,
    generate_refined_speech
)
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

    # =========================================================================
    # SECTION 1: BENCHMARK CONCEPT & INTERACTIVE PRACTICE PROMPTS
    # =========================================================================
    st.markdown("### 1️⃣ Target Concept & Guided Practice")
    col_concept, col_mode = st.columns([1.6, 1])

    current_concept_idx = 0
    if "selected_concept_override" in st.session_state and st.session_state["selected_concept_override"] in concept_names:
        current_concept_idx = concept_names.index(st.session_state["selected_concept_override"])

    with col_concept:
        selected_concept = st.selectbox(
            "🎯 Select Benchmark Topic to Explain:",
            concept_names,
            index=current_concept_idx,
            help="Choose the concept topic for evaluation."
        )

    with col_mode:
        st.write("")
        st.write("")
        practice_helper = st.toggle("Show Speaking Prompts & Tips", value=True)

    # Interactive Guided Speaking Prompts
    if practice_helper and selected_concept:
        prompts = get_topic_prompts(selected_concept)
        ref_text = concepts[selected_concept]["reference_text"]

        c_prompt1, c_prompt2 = st.columns([1.2, 1])
        with c_prompt1:
            with st.container(border=True):
                st.markdown(f"**🎯 3-Part Guided Speaking Prompt for `{selected_concept}`:**")
                st.caption("Try structuring your answer using these 3 key points:")
                for p in prompts:
                    st.markdown(f'<div class="prompt-card"><span class="prompt-step">Prompt</span> {p}</div>', unsafe_allow_html=True)

        with c_prompt2:
            with st.container(border=True):
                st.markdown("**⏱️ Target Speaking Goal:**")
                target_duration = st.select_slider(
                    "Target Explanation Length:",
                    options=["30 seconds", "45 seconds (Recommended)", "60 seconds", "90 seconds"],
                    value="45 seconds (Recommended)"
                )
                if "30" in target_duration:
                    st.info("🎯 **Target:** ~60-75 words. Focus on the core definition and 1 key principle.")
                elif "45" in target_duration:
                    st.info("🎯 **Target:** ~95-115 words. Definition + how it works + 1 real example.")
                else:
                    st.info("🎯 **Target:** ~130-160 words. In-depth explanation with technical depth.")

                with st.expander("📖 View Ground-Truth Reference Definition"):
                    st.markdown(f'*" {ref_text} "*')

    st.markdown("---")

    # =========================================================================
    # SECTION 2: MULTI-MODAL VOICE INPUT & AUDIO INSPECTOR
    # =========================================================================
    st.markdown("### 2️⃣ Voice Input & Recording")
    
    tab_mic, tab_upload, tab_sample = st.tabs([
        "🎙️ Record Live Voice",
        "📁 Upload Audio File",
        "⚡ Quick Demo Presets"
    ])

    if "active_audio_path" not in st.session_state:
        st.session_state["active_audio_path"] = None
    if "active_audio_label" not in st.session_state:
        st.session_state["active_audio_label"] = "voice_input.wav"

    with tab_mic:
        st.caption("Record your spoken explanation directly using your device microphone.")
        mic_audio = st.audio_input("Click microphone to record explanation:", key="evaluator_live_mic")
        if mic_audio is not None:
            if mic_audio.size > 500:
                os.makedirs("uploads", exist_ok=True)
                import uuid
                live_path = os.path.join("uploads", f"live_{uuid.uuid4().hex[:8]}.wav")
                with open(live_path, "wb") as f:
                    f.write(mic_audio.getbuffer())
                st.session_state["active_audio_path"] = live_path
                st.session_state["active_audio_label"] = "Live Microphone Recording"
            else:
                st.warning("⚠️ Recording was empty (0 bytes). Please ensure microphone access is allowed in your browser.")

    with tab_upload:
        st.caption("Upload a pre-recorded audio file (WAV, MP3, M4A, OGG).")
        uploaded_file = st.file_uploader(
            "Choose audio file",
            type=["wav", "mp3", "m4a", "ogg"],
            key="evaluator_file_upload",
            label_visibility="collapsed"
        )
        if uploaded_file is not None and uploaded_file.size > 500:
            up_path = save_uploaded_audio(uploaded_file)
            st.session_state["active_audio_path"] = up_path
            st.session_state["active_audio_label"] = uploaded_file.name

    with tab_sample:
        st.caption("Test the end-to-end evaluation with pre-recorded speech samples:")
        c_s1, c_s2 = st.columns(2)
        with c_s1:
            if st.button("🚀 Load Sample: Machine Learning (Fluent)", key="btn_sample_ml", use_container_width=True):
                st.session_state["active_audio_path"] = "data/samples/sample_machine_learning.wav"
                st.session_state["active_audio_label"] = "sample_machine_learning.wav (Fluent)"
                st.session_state["selected_concept_override"] = "Machine Learning"
                st.rerun()

        with c_s2:
            if st.button("☁️ Load Sample: Cloud Computing (With Fillers: um, basically)", key="btn_sample_cloud", use_container_width=True):
                st.session_state["active_audio_path"] = "data/samples/sample_cloud_computing.wav"
                st.session_state["active_audio_label"] = "sample_cloud_computing.wav (With Fillers)"
                st.session_state["selected_concept_override"] = "Cloud Computing"
                st.rerun()

    audio_path = st.session_state.get("active_audio_path")
    audio_source_label = st.session_state.get("active_audio_label", "voice_input.wav")

    # Audio Playback & Preview
    if audio_path and os.path.exists(audio_path) and os.path.getsize(audio_path) > 500:
        with st.container(border=True):
            col_ap1, col_ap2 = st.columns([2, 1])
            with col_ap1:
                st.markdown(f"**🔊 Audio Input Ready:** `{audio_source_label}`")
                st.audio(audio_path)
            with col_ap2:
                file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
                st.metric("📦 Audio File Size", f"{file_size_mb:.2f} MB")
                st.caption("Ready for multi-modal feature extraction.")

        # Trigger Evaluation
        analyze_btn = st.button("🚀 Run AI Conceptual Evaluation", type="primary", key="btn_run_evaluation", use_container_width=True)
    else:
        analyze_btn = False
        st.info("👆 **No active audio input selected:** Record your voice above, upload an audio file, or click a **Quick Demo Preset**.")

    # =========================================================================
    # PIPELINE EXECUTION
    # =========================================================================
    if analyze_btn and audio_path:
        with st.status("🧠 Processing Multi-Modal Speech Evaluation...", expanded=True) as status:
            try:
                st.write("🎙️ [1/5] Transcribing speech using OpenAI Whisper...")
                transcript = transcribe_audio(audio_path)

                if not transcript or not transcript.strip():
                    transcript = "No distinct spoken explanation was detected in the audio file."
                    st.warning("⚠️ Microphone input was very low or unclear. Analyzing acoustic signal and continuing.")

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
                    waveform_path=waveform_path,
                    candidate_name=st.session_state.get("custom_candidate_name", "Candidate")
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

                status.update(label="✅ Conceptual Evaluation Complete! Scroll down to explore your dashboard.", state="complete", expanded=True)
                st.toast("🎉 Evaluation Complete! View results below.", icon="✅")
            except Exception as e:
                import traceback
                err_tb = traceback.format_exc()
                status.update(label=f"❌ Evaluation Error: {e}", state="error", expanded=True)
                st.error(f"**Pipeline Error Occurred:** {e}")
                with st.expander("🔍 Diagnostic Details & Traceback", expanded=True):
                    st.code(err_tb, language="python")
                    st.info("💡 **Streamlit Cloud Note:** If you recently pushed new packages, click **Manage app -> '...' -> Reboot app** to make sure Linux OS packages are installed.")

    # =========================================================================
    # SECTION 3: INTERACTIVE RESULTS DASHBOARD
    # =========================================================================
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

        # ---------------------------------------------------------------------
        # INTERACTIVE RUBRIC WEIGHT SIMULATOR (WHAT-IF CALCULATOR)
        # ---------------------------------------------------------------------
        with st.expander("⚖️ Interactive Rubric Weight Simulator (What-If Calculator)", expanded=False):
            st.markdown("Experiment with different evaluation weights to see how your score adapts to various assessment contexts:")
            
            c_preset1, c_preset2, c_preset3 = st.columns(3)
            with c_preset1:
                if st.button("🎓 Academic Viva (70% Concept / 20% Fluency / 10% Clarity)", use_container_width=True):
                    st.session_state["w_sem"] = 70
                    st.session_state["w_flu"] = 20
                    st.session_state["w_cla"] = 10
            with c_preset2:
                if st.button("💼 Tech Interview (50% Concept / 25% Fluency / 25% Clarity)", use_container_width=True):
                    st.session_state["w_sem"] = 50
                    st.session_state["w_flu"] = 25
                    st.session_state["w_cla"] = 25
            with c_preset3:
                if st.button("⚖️ Balanced Default (60% Concept / 25% Fluency / 15% Clarity)", use_container_width=True):
                    st.session_state["w_sem"] = 60
                    st.session_state["w_flu"] = 25
                    st.session_state["w_cla"] = 15

            col_w1, col_w2, col_w3 = st.columns(3)
            with col_w1:
                w_sem = st.slider("Semantic Alignment Weight (%)", 10, 90, st.session_state.get("w_sem", 60), 5)
            with col_w2:
                w_flu = st.slider("Speech Fluency Weight (%)", 10, 90, st.session_state.get("w_flu", 25), 5)
            with col_w3:
                w_cla = st.slider("Articulation Clarity Weight (%)", 10, 90, st.session_state.get("w_cla", 15), 5)

            total_weight = w_sem + w_flu + w_cla
            simulated_score = round(
                (scores["Semantic Score"] * w_sem + scores["Fluency Score"] * w_flu + scores["Communication Score"] * w_cla) / total_weight,
                1
            )

            # Simulated tier
            if simulated_score >= 85:
                sim_tier = "Advanced Mastery"
            elif simulated_score >= 70:
                sim_tier = "Competent Understanding"
            elif simulated_score >= 50:
                sim_tier = "Developing Understanding"
            else:
                sim_tier = "Needs Foundational Focus"

            c_sim1, c_sim2 = st.columns([1, 2])
            with c_sim1:
                st.metric("Simulated Overall Score", f"{simulated_score} / 100", delta=f"{simulated_score - scores['Final Score']:+.1f} vs Default")
            with c_sim2:
                st.markdown(f"**Simulated Tier Under Current Weights:**<br>{render_tier_badge(sim_tier)}", unsafe_allow_html=True)

        st.markdown("---")

        # =====================================================================
        # 5 DETAILED INTERACTIVE TABS
        # =====================================================================
        tab_trans, tab_skills, tab_acoustic, tab_coach, tab_export = st.tabs([
            "📝 Transcript & Fillers",
            "🕸️ Competency Radar",
            "🎧 Acoustic Dynamics",
            "💡 AI Diagnostic Coaching",
            "📄 Official PDF Report"
        ])

        # ---------------------------------------------------------------------
        # TAB 1: INTERACTIVE TRANSCRIPT & FILLERS
        # ---------------------------------------------------------------------
        with tab_trans:
            raw_tr = res["transcript"]
            detected_fillers = fillers.get("Detected Fillers", {})

            st.markdown("#### Spoken Explanation Transcript & Lexical Inspector")

            # Interactive Filter Controls
            c_tf1, c_tf2 = st.columns([1.5, 1])
            with c_tf1:
                available_fillers = list(detected_fillers.keys())
                selected_filler_filters = st.multiselect(
                    "🎯 Highlight Specific Filler Words:",
                    options=available_fillers,
                    default=available_fillers,
                    help="Select which filler words to flag in red tags in the transcript below."
                )

            with c_tf2:
                search_word = st.text_input("🔍 Word Frequency Search:", placeholder="e.g. data, algorithm...")

            # Highlight logic
            highlighted_tr = raw_tr
            if selected_filler_filters:
                for word in selected_filler_filters:
                    pattern = re.compile(r"\b(" + re.escape(word) + r")\b", re.IGNORECASE)
                    highlighted_tr = pattern.sub(r'<span class="filler-tag">\1</span>', highlighted_tr)

            if search_word.strip():
                s_pattern = re.compile(r"\b(" + re.escape(search_word.strip()) + r")\b", re.IGNORECASE)
                occurrences = len(re.findall(s_pattern, raw_tr))
                highlighted_tr = s_pattern.sub(r'<span class="search-highlight-tag">\1</span>', highlighted_tr)
                st.info(f"Term **'{search_word}'** found **{occurrences}** times in spoken explanation.")

            # Display Transcript Box
            st.markdown(
                f'<div class="transcript-card">{highlighted_tr if highlighted_tr else "No transcript detected."}</div>',
                unsafe_allow_html=True
            )
            st.caption("🚩 Red tags: Detected verbal crutches  |  🟨 Gold tags: Search matches")

            # Interactive Speech Polish Tool
            st.markdown("---")
            with st.expander("✨ Interactive Speech Polish (Executive-Level Delivery)", expanded=False):
                st.caption("See how an expert or keynote speaker would state your explanation with zero filler words and elevated phrasing:")
                refined_text = generate_refined_speech(raw_tr, detected_fillers)
                
                c_ref1, c_ref2 = st.columns(2)
                with c_ref1:
                    st.markdown("**Your Spoken Version:**")
                    st.markdown(f'<div style="background:#1E293B; padding:12px; border-radius:8px; font-size:0.92rem; color:#94A3B8;">{raw_tr}</div>', unsafe_allow_html=True)
                with c_ref2:
                    st.markdown("**Polished Executive Delivery:**")
                    st.markdown(f'<div style="background:#111827; border-left:3px solid #10B981; padding:12px; border-radius:8px; font-size:0.92rem; color:#E5E7EB;">{refined_text}</div>', unsafe_allow_html=True)

            # Filler Words Distribution
            if detected_fillers:
                st.markdown("#### Filler Word Frequency Breakdown")
                c_fpie, c_fstats = st.columns([1, 1.2])
                with c_fpie:
                    st.plotly_chart(filler_words_pie(detected_fillers), use_container_width=True)
                with c_fstats:
                    st.write(f"Total Words Spoken: **{fillers['Total Words']}**")
                    st.write(f"Fillers Flagged: **{fillers['Filler Count']}** ({fillers['Filler Ratio']}%)")
                    for w, count in detected_fillers.items():
                        st.markdown(f"- Verbal crutch **'{w}'**: used **{count}** times")
            else:
                st.success("🎉 Flawless! Zero filler words detected in your explanation.")

        # ---------------------------------------------------------------------
        # TAB 2: COMPETENCY RADAR
        # ---------------------------------------------------------------------
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

        # ---------------------------------------------------------------------
        # TAB 3: ACOUSTIC DYNAMICS & PACE ARCHETYPE
        # ---------------------------------------------------------------------
        with tab_acoustic:
            a1, a2, a3, a4 = st.columns(4)
            a1.metric("Duration", f"{feats['Duration']} s")
            a2.metric("Speech Rate", f"{feats['Speech Rate']} WPM")
            a3.metric("Pause Ratio", f"{feats['Pause Ratio']*100:.1f}%")
            a4.metric("Mean Pitch", f"{feats['Pitch']} Hz")

            # Interactive Pace Archetype Meter
            st.markdown("#### 🏃 Speech Rate Archetype Meter")
            wpm = feats["Speech Rate"]
            
            if wpm < 105:
                archetype = "🐢 Deliberate / Hesitant (<105 WPM)"
                archetype_tip = "Consider increasing tempo to sound more confident and keep listener engagement."
            elif 105 <= wpm < 130:
                archetype = "🎓 Academic Lecturer (105-130 WPM)"
                archetype_tip = "Clear and methodical tempo, suitable for complex introductory concepts."
            elif 130 <= wpm <= 165:
                archetype = "🎙️ TED / Executive Speaker (130-165 WPM) - Optimal"
                archetype_tip = "Outstanding! This is the gold-standard pace for technical presentations."
            else:
                archetype = "🏎️ Fast Pitch / Rapid (>165 WPM)"
                archetype_tip = "Consider slowing down slightly so listeners can absorb dense technical definitions."

            with st.container(border=True):
                st.markdown(f"**Your Speech Archetype:** `{archetype}`")
                st.progress(min(1.0, max(0.0, wpm / 200.0)))
                st.caption(f"💡 **Coach Advice:** {archetype_tip}")

            st.markdown("#### Acoustic Waveform Visual")
            if res.get("waveform_path") and os.path.exists(res["waveform_path"]):
                st.image(res["waveform_path"], use_container_width=True)

        # ---------------------------------------------------------------------
        # TAB 4: INTERACTIVE AI COACHING & FLASHCARDS
        # ---------------------------------------------------------------------
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
                    for idx, sug_item in enumerate(fb["suggestions"]):
                        st.checkbox(f"{sug_item}", key=f"rec_check_{idx}", value=False)
                    st.caption("Check off items as you practice them for your next attempt!")

            # Interactive Concept Flashcards
            st.markdown("---")
            st.markdown("#### 📚 Interactive Concept Retention Flashcards")
            st.caption("Click any keyword to reveal why it is critical for mastering this topic:")

            c_f1, c_f2 = st.columns(2)
            with c_f1:
                st.markdown("**Matched Technical Terms:**")
                if fb["matched_keywords"]:
                    for kw in fb["matched_keywords"]:
                        with st.expander(f"✅ {kw.capitalize()}"):
                            st.write(get_keyword_flashcard_fact(kw, res["concept"]))
                else:
                    st.caption("No key vocabulary matches identified.")

            with c_f2:
                st.markdown("**Missed Core Concepts to Learn:**")
                if fb["missed_keywords"]:
                    for kw in fb["missed_keywords"]:
                        with st.expander(f"💡 {kw.capitalize()} (Learn Fact)"):
                            st.write(get_keyword_flashcard_fact(kw, res["concept"]))
                else:
                    st.caption("Excellent coverage of key reference vocabulary.")

            # Interactive Ask Coach Tool
            st.markdown("---")
            st.markdown("#### 🤖 Ask Concept Coach (Interactive Q&A)")
            st.caption("Get instant guidance on how to explain this topic effectively:")

            c_q1, c_q2, c_q3 = st.columns(3)
            q_answer = None

            with c_q1:
                if st.button("🚀 30s Elevator Pitch", use_container_width=True):
                    q_answer = get_topic_coach_answer(res["concept"], "pitch")
            with c_q2:
                if st.button("💡 Memorable Analogy", use_container_width=True):
                    q_answer = get_topic_coach_answer(res["concept"], "analogy")
            with c_q3:
                if st.button("⚠️ Common Pitfalls to Avoid", use_container_width=True):
                    q_answer = get_topic_coach_answer(res["concept"], "mistakes")

            if q_answer:
                st.info(f"**Coach Tip:** {q_answer}")

        # ---------------------------------------------------------------------
        # TAB 5: INTERACTIVE PDF REPORT CUSTOMIZER
        # ---------------------------------------------------------------------
        with tab_export:
            st.markdown("#### 📄 Customized Official PDF Assessment Report")
            st.caption("Personalize report parameters and metadata before generating your formal PDF certificate:")

            with st.container(border=True):
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    custom_candidate = st.text_input("Candidate / Student Name:", value=st.session_state.get("custom_candidate_name", "Alex Developer"))
                    st.session_state["custom_candidate_name"] = custom_candidate
                with col_p2:
                    custom_org = st.text_input("Organization / Institution:", value="Voice Concept Intelligence Platform")

                c_tog1, c_tog2 = st.columns(2)
                with c_tog1:
                    inc_waveform = st.checkbox("Include Acoustic Waveform Graph", value=True)
                with c_tog2:
                    inc_coaching = st.checkbox("Include AI Coaching Recommendations", value=True)

                if st.button("🔄 Update & Re-Generate Custom PDF", type="secondary"):
                    new_pdf_path = generate_pdf_report(
                        topic=res["concept"],
                        transcript=res["transcript"],
                        features=feats,
                        filler_result=fillers,
                        semantic_result=sem,
                        score_result=scores,
                        strengths=fb["strengths"],
                        suggestions=fb["suggestions"],
                        waveform_path=res.get("waveform_path"),
                        candidate_name=custom_candidate,
                        evaluator_org=custom_org,
                        include_waveform=inc_waveform,
                        include_coaching=inc_coaching
                    )
                    res["pdf_path"] = new_pdf_path
                    st.success("✅ PDF Report updated with custom parameters!")

            # Download Action
            pdf_path = res.get("pdf_path")
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                st.download_button(
                    label=f"📥 Download Assessment Report for '{st.session_state.get('custom_candidate_name', 'Candidate')}' (PDF)",
                    data=pdf_bytes,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.warning("PDF report is being generated...")

render_evaluator()
