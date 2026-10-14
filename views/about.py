import streamlit as st

def render_about():
    st.markdown(
        """
        <div class="app-header">
            <span class="header-badge">Architecture & Specs</span>
            <h1 class="header-title">System Architecture & AI Methodology</h1>
            <p class="header-subtitle">In-depth technical specifications of the multi-modal speech evaluation pipeline, neural embedding models, and mathematical rubrics.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    t1, t2, t3 = st.tabs([
        "🏗️ Architecture Pipeline",
        "🧮 Mathematical Scoring Rubric",
        "🤖 AI Model Specifications"
    ])

    with t1:
        st.subheader("Multi-Modal Speech Evaluation Pipeline")
        st.markdown(
            """
            ```mermaid
            graph LR
                A[Voice Input: Mic / Audio File] --> B[OpenAI Whisper Engine]
                A --> C[Librosa DSP Signal Engine]
                B --> D[Text Transcript]
                C --> E[Acoustic Features: WPM, Pause, Pitch, RMS]
                D --> F[Filler Word & Hesitation Detector]
                D --> G[Sentence-BERT Dense Encoder]
                H[(Benchmark Knowledge Base)] --> G
                G --> I[Cosine Semantic Similarity]
                E & F & I --> J[Synthesized Scoring Engine]
                J --> K[Interactive Dashboard]
                J --> L[Official PDF Report Generator]
                J --> M[(SQLite Audit History DB)]
            ```
            """
        )

        st.markdown("---")
        st.markdown(
            """
            ### Pipeline Stages:
            1. **Audio Acquisition**: Accepts multi-format audio files (WAV, MP3, M4A, OGG) or live microphone capture.
            2. **Acoustic Signal Processing**: Librosa analyzes raw waveforms to extract energy (RMS), silence distributions, zero-crossing rates, and pitch contours.
            3. **Automatic Speech Recognition (ASR)**: OpenAI Whisper transcribes speech into text with high accuracy even with varied accents.
            4. **Lexical Hesitation Analysis**: Regex tokenization matches common verbal crutches (`um`, `uh`, `like`, `you know`, `basically`).
            5. **Dense Semantic Embedding**: Sentence-BERT (`all-MiniLM-L6-v2`) encodes both explanation and reference ground truth into 384-dimensional dense vectors to calculate true conceptual cosine proximity.
            6. **Weighted Synthesis & Reporting**: Multimodal metrics are weighted into an overall mastery grade, and persisted with an automated PDF generation pass.
            """
        )

    with t2:
        st.subheader("Mathematical Scoring Formulations")

        st.markdown(
            r"""
            The **Overall Conceptual Mastery Score** is computed as a weighted linear combination:

            $$\text{Overall Score} = 0.60 \cdot S_{\text{Semantic}} + 0.25 \cdot S_{\text{Fluency}} + 0.15 \cdot S_{\text{Clarity}}$$

            ---

            #### 1. Semantic Conceptual Alignment ($S_{\text{Semantic}}$)
            Computed using cosine similarity between the candidate explanation vector $\mathbf{u}$ and benchmark vector $\mathbf{r}$:

            $$S_{\text{Semantic}} = \max\left(0, \frac{\mathbf{u} \cdot \mathbf{r}}{\|\mathbf{u}\| \|\mathbf{r}\|} \times 100\right)$$

            ---

            #### 2. Speaking Fluency & Cadence ($S_{\text{Fluency}}$)
            Evaluates speaking rate (Words Per Minute) against the optimal technical presentation range of **115 - 165 WPM**, penalized for prolonged silence:

            $$S_{\text{Fluency}} = 100 - \Delta_{\text{Pace}} - \text{Penalty}_{\text{Pause}}$$

            $$\text{where } \Delta_{\text{Pace}} = 
            \begin{cases} 
            (115 - \text{WPM}) \times 0.35 & \text{if WPM} < 115 \\
            (\text{WPM} - 165) \times 0.35 & \text{if WPM} > 165 \\
            0 & \text{otherwise}
            \end{cases}$$

            $$\text{and } \text{Penalty}_{\text{Pause}} = \max(0, (\text{Pause Ratio} - 0.25) \times 60.0)$$

            ---

            #### 3. Articulation Clarity ($S_{\text{Clarity}}$)
            Penalizes density of verbal crutches and fillers:

            $$S_{\text{Clarity}} = \max(0, 100 - 6.0 \times \text{Filler Ratio})$$
            """
        )

    with t3:
        st.subheader("Core Technology Specifications")

        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown("### 🎙️ OpenAI Whisper")
                st.write("**Architecture:** Encoder-Decoder Transformer")
                st.write("**Model Variant:** `base` (74 Million Parameters)")
                st.write("**Capabilities:** Multilingual speech-to-text, background noise robustness")

            with st.container(border=True):
                st.markdown("### 🎧 Librosa Audio DSP")
                st.write("**Core Function:** Acoustic Signal Processing")
                st.write("**Algorithms:** PiPTRACK pitch tracking, RMS Energy, Short-Time Fourier Transform (STFT)")

        with c2:
            with st.container(border=True):
                st.markdown("### 🧠 Sentence-BERT")
                st.write("**Model:** `all-MiniLM-L6-v2`")
                st.write("**Embedding Dimension:** 384 dimensions")
                st.write("**Training:** 1 Billion sentence pairs for semantic search and clustering")

            with st.container(border=True):
                st.markdown("### 📄 ReportLab PDF Engine")
                st.write("**Engine:** Platypus Document Flow Engine")
                st.write("**Output:** Vector PDF with table styles and embedded acoustic graphs")

render_about()
