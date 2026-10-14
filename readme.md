# 🎙️ Voice Based Concept Understanding Analyser (VBCUA)

An enterprise-grade AI speech intelligence platform that evaluates a speaker's conceptual understanding by listening to and analyzing their spoken explanations.

Built with **Streamlit**, **OpenAI Whisper**, **Sentence-BERT**, **Librosa DSP**, and **Plotly**.

---

## 🚀 Key Features

- 🎙️ **Multi-Modal Voice Input**:
  - Live microphone recording directly in the browser (`st.audio_input`).
  - Audio file upload (`.wav`, `.mp3`, `.m4a`, `.ogg`).
  - Built-in 1-click **Quick Demo Presets** for instant testing without needing audio files.
- 📝 **Neural Speech-to-Text**:
  - Accurate speech transcription powered by **OpenAI Whisper** (`base` model).
  - Handles diverse accents, technical terminology, and background noise.
- 🎧 **Acoustic Signal Processing (DSP)**:
  - Speaking pace calculation (Words Per Minute / WPM).
  - Pause and silence ratio detection.
  - Mean pitch contour extraction and RMS energy.
  - High-resolution acoustic waveform visualization via **Librosa**.
- 💬 **Hesitation & Filler Word Analysis**:
  - Scans transcripts for verbal crutches (*"um"*, *"uh"*, *"like"*, *"basically"*, *"you know"*, etc.).
  - Calculates filler density ratios and highlights fillers inline in the transcript.
- 🧠 **Dense Semantic Alignment**:
  - Encodes explanations and reference definitions into 384-dimensional dense vectors using **Sentence-BERT** (`all-MiniLM-L6-v2`).
  - Computes cosine similarity to evaluate true conceptual understanding beyond simple keyword matching.
- 🏆 **Intelligent Multi-Modal Scoring**:
  - Weighted synthesis: **60% Semantic Alignment + 25% Speaking Fluency + 15% Articulation Clarity**.
  - Performance tier classification:
    - `🟢 Advanced Mastery` (85–100%)
    - `🟡 Competent Understanding` (70–84.9%)
    - `🟠 Developing Understanding` (50–69.9%)
    - `🔴 Needs Foundational Focus` (<50%)
- 💡 **AI Diagnostic Coaching**:
  - Identifies matched technical keywords vs. missed conceptual terms.
  - Actionable feedback on speech cadence, pauses, and conceptual depth.
- 📊 **Executive Analytics Dashboard**:
  - Competency radar profile across semantic, pace, articulation, and acoustic balance.
  - Cohort score progression and grade distribution charts.
- 📄 **Standardized PDF Assessment Reports**:
  - Publication-ready PDF generation with tables, metrics, waveform visuals, and recommendations using **ReportLab**.
- 📜 **Audit History & Search**:
  - Automatically logs every evaluation into a local **SQLite** database for auditing and re-downloading past reports.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend / UI** | Streamlit, Plotly, HTML5/CSS3 (Obsidian Dark Theme) |
| **Speech Recognition** | OpenAI Whisper, PyTorch |
| **Semantic AI** | Sentence-BERT (`sentence-transformers`), Hugging Face |
| **Audio DSP** | Librosa, NumPy, SciPy, Matplotlib |
| **Report Engine** | ReportLab |
| **Database** | SQLite3 |

---

## 🧮 Scoring Formula

$$\text{Final Score} = 0.60 \times S_{\text{Semantic}} + 0.25 \times S_{\text{Fluency}} + 0.15 \times S_{\text{Clarity}}$$

1. **Semantic Score ($S_{\text{Semantic}}$)**: Cosine similarity of dense vector embeddings:
   $$S_{\text{Semantic}} = \max\left(0, \frac{\mathbf{u} \cdot \mathbf{r}}{\|\mathbf{u}\| \|\mathbf{r}\|} \times 100\right)$$
2. **Fluency Score ($S_{\text{Fluency}}$)**: Evaluated against optimal technical pace of **115–165 WPM**, penalized for prolonged silences (>25%).
3. **Clarity Score ($S_{\text{Clarity}}$)**: Penalizes verbal crutches and filler density:
   $$S_{\text{Clarity}} = \max(0, 100 - 6.0 \times \text{Filler Ratio})$$

---

## 📁 Project Structure

```
├── app.py                     # Main application entrypoint (st.navigation)
├── .streamlit/
│   └── config.toml            # Dark theme configuration
├── views/
│   ├── evaluator.py           # Core Voice Evaluator workspace
│   ├── dashboard.py           # Analytics & Insights Dashboard
│   ├── history.py             # Assessment History & Audit Log
│   ├── concepts.py            # Benchmark Concept Knowledge Base
│   └── about.py               # Technical Specs & Architecture
├── modules/
│   ├── speech_to_text.py      # Whisper STT engine
│   ├── semantic_eval.py       # Sentence-BERT cosine similarity
│   ├── feature_extractor.py   # Librosa acoustic signal processor
│   ├── filler_word.py         # Hesitation & filler word detector
│   ├── scoring_engine.py      # Multi-modal scoring & rubric
│   ├── feedback_engine.py     # AI diagnostic coaching & keyword analysis
│   ├── dashboard.py           # Plotly visualization charts
│   ├── report_generator.py    # ReportLab PDF generator
│   └── audio_utils.py         # Waveform plotting & audio utilities
├── database/
│   └── db.py                  # SQLite history & audit manager
├── data/
│   └── samples/               # Built-in demo audio clips for 1-click testing
├── models/
│   └── reference_concepts.json# Ground-truth concept benchmarks
├── styles/
│   └── style.css              # Custom modern UI styling
├── test_ui.py                 # Automated pipeline verification suite
└── requirements.txt           # Python dependencies
```

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/suryamouli09/Voice-Based-Concept-Understanding-Analyser.git
cd Voice-Based-Concept-Understanding-Analyser
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux / macOS:
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note**: OpenAI Whisper uses `ffmpeg` for audio decoding. Make sure `ffmpeg` is installed on your system.

### 4. Run the application
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your web browser.

---

## 🧪 Automated Testing

To test the entire pipeline end-to-end:
```bash
python test_ui.py
```

---

## 📄 License
MIT License. Developed for automated conceptual voice evaluation.