import os
import numpy as np
import streamlit as st
import whisper

def load_audio_array(audio_path: str) -> np.ndarray:
    """
    Load an audio file into a 16kHz float32 mono numpy array.
    This bypasses the ffmpeg subprocess dependency when reading WAV/FLAC/OGG files,
    allowing seamless operation in lightweight cloud containers.
    """
    # Attempt 1: soundfile (fast, zero external binaries needed for WAV/FLAC/OGG)
    try:
        import soundfile as sf
        data, sr = sf.read(audio_path, dtype="float32")
        if data.ndim > 1:
            data = data.mean(axis=1)
        if sr != 16000:
            import librosa
            data = librosa.resample(data, orig_sr=sr, target_sr=16000)
        return data.astype(np.float32)
    except Exception:
        pass

    # Attempt 2: librosa.load
    try:
        import librosa
        y, _ = librosa.load(audio_path, sr=16000, mono=True)
        return y.astype(np.float32)
    except Exception:
        pass

    # If both in-memory decoders fail, return None so Whisper can try native path loading
    return None

@st.cache_resource(show_spinner="Loading Whisper Speech Recognition Engine...")
def _load_whisper_model(model_name: str = "tiny"):
    """
    Load and cache the Whisper model in memory.
    Using 'tiny' ensures fast CPU inference (~1-2s) and minimal RAM footprint (<100MB),
    guaranteeing stability under Streamlit Cloud's 1GB memory cap.
    """
    return whisper.load_model(model_name, device="cpu")

def transcribe_audio(audio_path: str, model_size: str = "tiny") -> str:
    """
    Transcribe an audio file using OpenAI Whisper.
    Accepts direct 16kHz float32 audio arrays or file paths.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Guard against 0-byte or empty audio recordings
    if os.path.getsize(audio_path) < 500:
        return ""

    # Allow environment override if specified
    active_model = os.getenv("WHISPER_MODEL", model_size)
    model = _load_whisper_model(active_model)

    # 1. Attempt decoding into memory array to bypass system ffmpeg requirement
    audio_data = load_audio_array(audio_path)

    if audio_data is not None and len(audio_data) > 0:
        result = model.transcribe(audio_data, fp16=False)
    else:
        # 2. Fallback to file path transcription (requires ffmpeg installed)
        result = model.transcribe(audio_path, fp16=False)

    transcript = result.get("text", "").strip()

    # Save transcript backup
    os.makedirs("outputs/transcripts", exist_ok=True)
    transcript_file = os.path.join("outputs", "transcripts", "latest_transcript.txt")
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(transcript)

    return transcript