import os
import librosa
import numpy as np

def extract_audio_features(audio_path: str, transcript: str = "") -> dict:
    """
    Extracts acoustic signal processing features using Librosa:
    - Duration (seconds)
    - Speech Rate (Words Per Minute)
    - RMS Energy
    - Zero Crossing Rate
    - Pause / Silence Ratio
    - Mean Pitch (Hz)
    """
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 500:
        return {
            "Duration": 0.0,
            "Speech Rate": 0.0,
            "RMS Energy": 0.0,
            "Zero Crossing Rate": 0.0,
            "Silence Ratio": 0.0,
            "Pause Ratio": 0.0,
            "Pitch": 0.0
        }

    try:
        y, sr = librosa.load(audio_path, sr=None)
    except Exception:
        y = np.zeros(16000)
        sr = 16000

    total_samples = len(y)
    duration = float(librosa.get_duration(y=y, sr=sr)) if total_samples > 0 else 0.0

    # 1. RMS Energy
    rms = librosa.feature.rms(y=y)[0] if total_samples > 0 else np.array([0.0])
    rms_energy = float(np.mean(rms))

    # 2. Zero Crossing Rate
    zcr = librosa.feature.zero_crossing_rate(y)[0] if total_samples > 0 else np.array([0.0])
    zero_cross_rate = float(np.mean(zcr))

    # 3. Silence and Pause Ratio (energy threshold method)
    threshold = 0.025
    silent_samples = int(np.sum(np.abs(y) < threshold))
    silence_ratio = float(silent_samples / total_samples) if total_samples > 0 else 0.0
    pause_ratio = silence_ratio

    # 4. Pitch Extraction
    mean_pitch = 0.0
    try:
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = pitches[pitches > 0]
        if len(pitch_values) > 0:
            mean_pitch = float(np.mean(pitch_values))
    except Exception:
        mean_pitch = 0.0

    # 5. Speech Rate (Words per minute)
    words = len(transcript.split()) if transcript else 0
    if duration > 0:
        speech_rate = float((words / duration) * 60.0)
    else:
        speech_rate = 0.0

    return {
        "Duration": round(duration, 2),
        "Speech Rate": round(speech_rate, 1),
        "RMS Energy": round(rms_energy, 4),
        "Zero Crossing Rate": round(zero_cross_rate, 4),
        "Silence Ratio": round(silence_ratio, 4),
        "Pause Ratio": round(pause_ratio, 4),
        "Pitch": round(mean_pitch, 1)
    }