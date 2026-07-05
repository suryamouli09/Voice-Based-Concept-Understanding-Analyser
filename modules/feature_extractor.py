import librosa
import numpy as np


def extract_audio_features(audio_path, transcript=""):

    # Load audio
    y, sr = librosa.load(audio_path, sr=None)

    # -----------------------------
    # Duration
    # -----------------------------
    duration = librosa.get_duration(y=y, sr=sr)

    # -----------------------------
    # RMS Energy
    # -----------------------------
    rms = librosa.feature.rms(y=y)[0]
    rms_energy = float(np.mean(rms))

    # -----------------------------
    # Zero Crossing Rate
    # -----------------------------
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    zero_cross_rate = float(np.mean(zcr))

    # -----------------------------
    # Silence Ratio
    # -----------------------------
    threshold = 0.02

    silent_samples = np.sum(np.abs(y) < threshold)

    silence_ratio = silent_samples / len(y)

    # -----------------------------
    # Pause Ratio
    # -----------------------------
    pause_ratio = silence_ratio

    # -----------------------------
    # Pitch
    # -----------------------------
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

    pitch_values = pitches[pitches > 0]

    if len(pitch_values) > 0:
        mean_pitch = float(np.mean(pitch_values))
    else:
        mean_pitch = 0

    # -----------------------------
    # Speech Rate
    # -----------------------------
    words = len(transcript.split())

    if duration > 0:
        speech_rate = (words / duration) * 60
    else:
        speech_rate = 0

    return {

        "Duration": round(duration, 2),

        "Speech Rate": round(speech_rate, 2),

        "RMS Energy": round(rms_energy, 4),

        "Zero Crossing Rate": round(zero_cross_rate, 4),

        "Silence Ratio": round(silence_ratio, 4),

        "Pause Ratio": round(pause_ratio, 4),

        "Pitch": round(mean_pitch, 2)

    }