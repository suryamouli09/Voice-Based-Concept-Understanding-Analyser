import os
import streamlit as st
import whisper

@st.cache_resource(show_spinner="Loading Whisper Speech Recognition Engine...")
def _load_whisper_model():
    """Load and cache the Whisper model in memory."""
    return whisper.load_model("base")

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe an audio file using OpenAI Whisper.
    Returns the cleaned transcription string.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    model = _load_whisper_model()
    # fp16=False prevents CPU warning on machines without CUDA
    result = model.transcribe(audio_path, fp16=False)
    transcript = result.get("text", "").strip()

    # Save transcript backup
    os.makedirs("outputs/transcripts", exist_ok=True)
    transcript_file = os.path.join("outputs", "transcripts", "latest_transcript.txt")
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(transcript)

    return transcript